// Validate the actual .xbp archive with the official spx interpreter and loaders.
package main

import (
 "archive/zip"
 "encoding/json"
 "fmt"
 "image/png"
 "io"
 "io/fs"
 "os"
 "path"
 "strings"
 spxfs "github.com/goplus/spx/v3/fs"
 project "github.com/goplus/spx/v3/internal/core/project"
 "github.com/goplus/spx/v3/pkg/ispx"
)
type assetDir struct{ z *zip.ReadCloser }
func(d assetDir) Open(p string)(io.ReadCloser,error){return d.z.Open(path.Join("assets",p))}
func(d assetDir) Close()error{return nil}
func(d assetDir) ReadDir(p string)([]spxfs.DirEntry,error){es,e:=fs.ReadDir(d.z,path.Join("assets",p));if e!=nil{return nil,e};return spxfs.DirEntriesFromFS(es),nil}
func must(err error){if err!=nil{panic(err)}}
func main(){
 if len(os.Args)!=2{fmt.Println("Usage: go run . /absolute/path/StarRailRunner.xbp");os.Exit(2)}
 z,err:=zip.OpenReader(os.Args[1]);must(err);defer z.Close()
 f,err:=z.Open("builder-meta.json");must(err);var m map[string]any;must(json.NewDecoder(f).Decode(&m));f.Close();if m["type"]!="game"{panic("invalid project type")}
 must(ispx.Init(nil));must(ispx.BuildFS(z));fmt.Println("PASS: all .spx scripts compile in official spx 3.3.0 interpreter")
 d:=assetDir{z};loaded,err:=project.LoadBuilderProject(d,nil);must(err)
 if loaded.Config.Width!=480||loaded.Config.Height!=360{panic("wrong viewport")}
 images:=0
 checkImage:=func(p string,w,h float64){f,e:=d.Open(p);must(e);defer f.Close();cfg,e:=png.DecodeConfig(f);must(e);if w>0&&(float64(cfg.Width)!=w||float64(cfg.Height)!=h){panic("image dimensions mismatch: "+p)};images++}
 for _,b:=range loaded.Project.Backdrops{checkImage(b.Path,b.ImageWidth,b.ImageHeight)}
 seen:=map[string]bool{}
 for _,v:=range loaded.Project.Zorder{
  name,ok:=v.(string);if !ok{panic("expected sprite name")};if seen[name]{panic("duplicate sprite")};seen[name]=true
  f,err:=z.Open(name+".spx");must(err);f.Close()
  s,err:=project.LoadSpriteConfig(d,name);must(err);if s.Config.Size!=0.5{panic("wrong sprite render scale: "+name)}
  for _,c:=range s.Config.Costumes{checkImage(c.Path,c.ImageWidth,c.ImageHeight)}
 }
 sounds:=0
 for _,f:=range z.File{if strings.HasPrefix(f.Name,"assets/sounds/")&&strings.HasSuffix(f.Name,"/index.json"){
  name:=strings.Split(f.Name,"/")[2];snd,err:=project.LoadSoundConfig(d,name);must(err);f,err:=d.Open(snd.Config.Path);must(err);b:=make([]byte,12);_,err=io.ReadFull(f,b);must(err);f.Close();if string(b[:4])!="RIFF"||string(b[8:12])!="WAVE"{panic("invalid WAV")};sounds++
 }}
 fmt.Printf("PASS: official project/resource loaders read %d sprites, %d PNG costume/backdrop files and %d sounds from .xbp\n",len(seen),images,sounds)
}
