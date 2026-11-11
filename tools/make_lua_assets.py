# Console batches: an "Assets_UI_Screens" timeline at 900x1860 with the five UI comps, rendered as PNG stills,
# then back to the master timeline. Forward slashes avoid escaping problems.
# usage (from vaultx/): python -I tools/make_lua_assets.py -> build/lua_assets.txt
import os

comps = os.path.abspath('build/comps').replace('\\', '/') + '/'
out = os.path.abspath('deliverables/assets/ui_screens').replace('\\', '/')
os.makedirs('deliverables/assets/ui_screens', exist_ok=True)
names = ['UI_01_Send', 'UI_02_Sent', 'UI_03_Swap', 'UI_04_Dashboard', 'UI_05_Splash']
L = []
L.append('mp=p:GetMediaPool();t2=mp:CreateEmptyTimeline("Assets_UI_Screens");p:SetCurrentTimeline(t2);'
         'print("custom",t2:SetSetting("useCustomSettings","1"),t2:SetSetting("timelineResolutionWidth","900"),'
         't2:SetSetting("timelineResolutionHeight","1860"),t2:GetSetting("timelineResolutionWidth"),t2:GetSetting("timelineResolutionHeight"))')
L.append('UI={%s};UIT={};for i,n in ipairs(UI) do t2:SetCurrentTimecode(TC((i-1)*150)); local x=t2:InsertFusionCompositionIntoTimeline(); '
         'x:ImportFusionComp("%s"..n..".comp"); x:SetName(n); UIT[i]=x end;s="";for i,x in ipairs(UIT) do s=s..x:GetName().."@"..(x:GetStart()-t2:GetStartFrame()).." " end;print(s)'
         % (','.join('"%s"' % n for n in names), comps))
L.append('p:DeleteAllRenderJobs();p:SetCurrentRenderFormatAndCodec("png","RGB8");for i,x in ipairs(UIT) do local f=x:GetStart()+75; '
         'p:SetRenderSettings({SelectAllFrames=false,MarkIn=f,MarkOut=f,TargetDir="%s",CustomName=x:GetName(),FormatWidth=900,FormatHeight=1860,ExportVideo=true,ExportAudio=false}); p:AddRenderJob() end;'
         'print("ui jobs",#p:GetRenderJobList(),p:StartRendering())' % out)
L.append('p:SetCurrentTimeline(tl);print("back",p:GetCurrentTimeline():GetName(),"save",resolve:GetProjectManager():SaveProject())')
open('build/lua_assets.txt', 'w', encoding='utf8').write('\n'.join(L) + '\n')
print(len(L), [len(x) for x in L])
