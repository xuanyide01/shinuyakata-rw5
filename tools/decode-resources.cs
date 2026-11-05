using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using System.IO.Compression;
using System.Reflection;
using System.Text;
using System.Security.Cryptography;
using GameRes.Formats.KiriKiri;

public static class DecodeYakataResources {
 // Interface-only work uses the fixed allowlist below. Original-file restore
 // is a separate, explicitly requested operation: no rendering, conversion,
 // new images/text generation, application packaging or network publication.
 static readonly HashSet<string> SafeInterface = new HashSet<string> {
  "AppConfig.tjs","main/Config.tjs","uipsd/title.csv","Config.tjs",
  "title.csv","message.csv","title.func","title_release.func",
  "conf.csv","file.csv","file_load.csv","file_save.csv","gallery.csv","backlog.csv"
 };
 static JavaScriptSerializer json=new JavaScriptSerializer {MaxJsonLength=200000000};
 static uint Adler(byte[] b) {
  uint a=1,c=0;int pos=0;
  while(pos<b.Length){int end=Math.Min(b.Length,pos+5552);for(;pos<end;pos++){a+=b[pos];c+=a;}a%=65521;c%=65521;}
  return(c<<16)|a;
 }
 static string Hash(byte[] b){using(var s=SHA256.Create())return BitConverter.ToString(s.ComputeHash(b)).Replace("-","").ToLowerInvariant();}
 static byte[] ReadExact(Stream s,int n){byte[] b=new byte[n];int p=0;while(p<n){int k=s.Read(b,p,n-p);if(k==0)throw new EndOfStreamException();p+=k;}return b;}
 public static void Run(string game,string manifest,string module,string output,string report,string mode) {
  var cipher=Xp3Opener.KnownSchemes["Shiniyuku Kimi, Yakata ni Mebuku Zouo"];
  byte[] tpm=File.ReadAllBytes(module),marker=Encoding.ASCII.GetBytes(" Encryption control block");int table=-1;
  for(int i=0;i<tpm.Length-4096;i+=4){if(tpm.Skip(i).Take(marker.Length).SequenceEqual(marker)){table=i;break;}}
  if(table<0)throw new Exception("Control table missing");
  uint[] words=new uint[1024];for(int i=0;i<1024;i++)words[i]=~BitConverter.ToUInt32(tpm,table+i*4);
  var blockField=typeof(CxEncryption).GetField("ControlBlock",BindingFlags.Instance|BindingFlags.NonPublic);
  if(blockField.GetValue(cipher)==null)blockField.SetValue(cipher,words);
  var entries=json.Deserialize<List<Dictionary<string,object>>>(File.ReadAllText(manifest));
  var rows=new List<object>();var errors=new List<object>();int done=0;
  foreach(var e in entries){string name=(string)e["name"],archive=(string)e["archive"];
   if(mode!="interface"&&mode!="verify-all-discard"&&mode!="restore-original-files")throw new Exception("Unsupported processing mode");
   if(mode=="interface"&&!SafeInterface.Contains(name))continue;
   try {
    string dest=Path.GetFullPath(Path.Combine(output,Path.GetFileNameWithoutExtension(archive),name.Replace('/',Path.DirectorySeparatorChar)));
    if(!dest.StartsWith(Path.GetFullPath(output)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase))throw new Exception("Unsafe path");
    byte[] raw;
    using(var f=File.OpenRead(Path.Combine(game,archive)))using(var combined=new MemoryStream()){
     foreach(ArrayList seg in (ArrayList)e["segments"]){f.Position=Convert.ToInt64(seg[1]);byte[] b=ReadExact(f,Convert.ToInt32(seg[3]));
      if((Convert.ToInt32(seg[0])&1)!=0){using(var ins=new MemoryStream(b,2,b.Length-6))using(var z=new DeflateStream(ins,CompressionMode.Decompress))using(var dst=new MemoryStream()){z.CopyTo(dst);b=dst.ToArray();}}
      if(b.Length!=Convert.ToInt32(seg[2]))throw new Exception("Segment length mismatch");combined.Write(b,0,b.Length);
     }raw=combined.ToArray();
    }
    if(raw.Length!=Convert.ToInt32(e["original"]))throw new Exception("Resource length mismatch");
    uint hash=Convert.ToUInt32(e["adler32"]);bool decoded=Adler(raw)!=hash;
    if(decoded)cipher.Decrypt(new Xp3Entry{Hash=hash,Name=name},0,raw,0,raw.Length);
    if(Adler(raw)!=hash)throw new Exception("Post-decode Adler mismatch");
    bool exported=(mode=="interface"&&SafeInterface.Contains(name))||mode=="restore-original-files";
    if(exported){
     Directory.CreateDirectory(Path.GetDirectoryName(dest));
     if(File.Exists(dest)){
      byte[] existing=File.ReadAllBytes(dest);
      if(existing.Length!=raw.Length||Hash(existing)!=Hash(raw))throw new Exception("Existing destination differs; refusing overwrite");
     }else File.WriteAllBytes(dest,raw);
    }
    rows.Add(new{archive=archive,name=name,bytes=raw.Length,sha256=Hash(raw),adler32=hash,adlerVerified=true,decoded=decoded,exported=exported});
    done++;if(done%100==0)Console.WriteLine("VERIFIED_RESOURCES "+done);
   } catch(Exception ex) {errors.Add(new{archive=archive,name=name,error=ex.GetType().Name+": "+ex.Message});}
  }
  Directory.CreateDirectory(Path.GetDirectoryName(report));
  File.WriteAllText(report,json.Serialize(new{result=errors.Count==0?"passed":"partial",method="GARbro official matching Cx profile and embedded game-specific control table; independent size/Adler/SHA-256",originalGameCodeExecuted=false,newStoryOrImagesGenerated=false,mode=mode,verified=done,failures=errors.Count,resources=rows,errors=errors}),new UTF8Encoding(false));
  Console.WriteLine("RESULT "+done+" verified; "+errors.Count+" failed");
 }
}
