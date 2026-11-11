# One-line Resolve Console setup (helpers used while building/rendering). usage: python -I tools/make_lua_setup.py
import os

root = os.path.abspath('.').replace('\\', '\\\\')
CP = root + '\\\\build\\\\comps\\\\'
setup = ('p=resolve:GetProjectManager():GetCurrentProject();tl=p:GetCurrentTimeline();CP="%s";'
         'function D(t) local o={};for k,v in pairs(t) do if type(v)=="userdata" then o[#o+1]=v end end;return o end;'
         'function TC(f) local s=math.floor(f/30); return string.format("01:%%02d:%%02d:%%02d", math.floor(s/60), s%%60, f%%30) end;'
         'V1=D(tl:GetItemListInTrack("video",1));'
         'function LOADC(item,nm) item:ImportFusionComp(CP..nm..".comp"); item:SetName(nm); return true end;'
         'function REIMP(only) local r="" for i,x in ipairs(V1) do local nm=x:GetName(); if (not only) or only[i] then LOADC(x,nm); r=r..i.." " end end return r end;'
         'function RJ(a,b,dir,name,fmt,codec,w,h,aud) p:SetCurrentRenderFormatAndCodec(fmt,codec); p:SetRenderSettings({SelectAllFrames=false,MarkIn=tl:GetStartFrame()+a,MarkOut=tl:GetStartFrame()+b,TargetDir=dir,CustomName=name,FormatWidth=w,FormatHeight=h,ExportVideo=true,ExportAudio=aud or false}); return p:AddRenderJob() end;'
         's="";for i,x in ipairs(V1) do s=s..i..":"..x:GetName().."@"..(x:GetStart()-tl:GetStartFrame()).."+"..x:GetDuration().." " end;print(s);'
         'c="";for k,v in pairs(p:GetRenderCodecs("mov")) do c=c..k.."="..v.."; " end;print("mov:",c)') % CP
open('build/lua_setup.txt', 'w', encoding='utf8').write(setup + '\n')
print(len(setup))
