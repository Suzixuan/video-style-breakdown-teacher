# pS_L7x9PaY1vXXSh Premiere 老师版逐转场拆解

分析范围：00:00:00.000–00:00:30.000  
源参数：1080×1920、25fps、AAC 44.1kHz  
教学版本：0.1.0  
证据模式：teacher  
证据数量：3张概览、6张事件表、1张波形；事件表每秒12.5张，即每隔2个源帧取1张

## 先看结论

这是一支“黑白金科幻产品广告”：它不是靠花哨转场插件串起来，而是用**形状匹配、极短插入帧、正负片反差、RGB故障包装和3D产品动画**不断把“角色—眼睛—表盘—机械结构”变成同一个视觉母题。

最值得先学的三个原则：

1. **先匹配形状，再加特效。** 圆形眼睛、表盘和机械环的位置接近，所以硬切也成立。
2. **用帧数控制冲击。** 1–3帧负责闪烁与惊吓，4–8帧负责看得见的动作，10–11帧约等于本片一拍。
3. **把素材能力和剪辑能力分开。** PR能复刻节奏、叠层、反相、RGB错位和HUD；真实的机械透视旋转来自3D源动画。

## 素材与证据

- 30秒共有约750个源帧；概览表抽取60帧，六个事件窗口合计抽取约90帧。事件表不是逐一覆盖全部源帧，时间步长为0.08秒≈2帧。
- 场景检测得到27个强变化帧，合并后是17个变化簇。故障闪帧会在一个转场内触发多次，因此不能说“有27个镜头”。
- 音频能量法给出的候选速度约252.1 BPM：一拍约0.24秒≈6帧，半拍约3帧。它是本套检测参数下的能量候选，不是人工确认的乐谱；本课节奏判断以帧数证据为准。
- 本次共使用9张视觉证据，属于中等 token 强度。按证据图、逐转场推理、长篇教学和教程检索综合估算，完整 `teacher` 流程约 **30k–70k model tokens（输入＋输出）**；只做概览的 `quick` 约10k–25k，逐源帧核对的 `forensic` 很容易超过80k。运行环境没有暴露精确计数，这些是规划区间，不是账单数字。

证据入口：

- [分析清单](evidence/analysis_manifest.json)
- [0–10秒概览](evidence/overview/overview-01-00-00-00-000.jpg)
- [10–20秒概览](evidence/overview/overview-02-00-00-10-000.jpg)
- [20–30秒概览](evidence/overview/overview-03-00-00-20-000.jpg)
- [音频波形](evidence/waveform.png)

## 节奏地图

| 时间 | 叙事/视觉任务 | 节奏单位（帧） | 主要连接方式 |
|---|---|---|---|
| 00:00–00:01.36 | 白底角色建立世界观 | 约34帧 | 主体居中、缓慢放大 |
| 00:01.36–00:03.00 | 角色与手表高速互切 | 2–5帧插入 | 圆形位置、黑白反差、声音瞬态 |
| 00:03.00–00:04.72 | 头盔到眼睛再到机械环 | 4–8帧推进 | 圆形形状匹配、中心推近 |
| 00:04.72–00:10.88 | 机械隧道与扫描角色 | 3–6帧 | 旋转方向、RGB故障、HUD层 |
| 00:10.88–00:15.00 | 卡片式展示零件 | 6–8帧 | 同一边框、主体替换、黑蓝背景交替 |
| 00:15.00–00:20.00 | 完整表体的产品英雄镜头 | 6–12帧 | 3D转台、微距尺度递进 |
| 00:20.00–00:22.00 | 表芯穿行到表背 | 3帧级切点 | 圆形结构、持续横向运动 |
| 00:22.00–00:26.00 | 手部互动与腕表展示 | 6–8帧 | 明暗反相、手势与物体关系 |
| 00:26.00–00:30.00 | 角色回归并缩小成剪影 | 12–18帧 | 中心构图、持续拉远、留白 |

## 逐转场教学

### T01 角色—表面纹理—腕表—角色的闪帧组接

**时间码证据**：00:00:01.360≈帧34仍是白底角色；00:00:01.440≈帧36切到黑色纹理；00:00:01.520≈帧38出现高亮腕表环；00:00:01.680≈帧42出现腕表；00:00:01.920≈帧48落回角色头盔。见[event-01](evidence/events/event-01-00-00-01-400.jpg)。  
**观察**：0.56秒内交替出现角色、黑底纹理和腕表，单个插入只持续约2–4帧；画面中心始终被圆形或头部占据，亮度在白—黑—白之间跳变。  
**判断与置信度**：这是“节拍闪帧＋形状匹配＋短插入蒙太奇”，置信度高；是否使用某个故障插件无法从成片确定。  
**原理**：眼睛来不及阅读细节，却能抓住中心位置和圆形轮廓。短插帧提供冲击，位置连续性负责让冲击不变成随机乱码。  
**Premiere 操作**：

1. 把音乐放到A1，显示波形，在00:00:01.24和00:00:01.96附近按`M`建立主标记。
2. 在V1放角色主镜头；把腕表和纹理素材放V2，切成2–4帧的小段，交替覆盖V1。
3. 冻结切点前后画面，临时把V2不透明度降到50%，用`Effect Controls > Motion > Position/Scale`让圆形中心重合。
4. 需要白闪时，在V4放白色Color Matte，只留1帧；需要黑闪时优先用素材本身的暗帧，不要随意插空黑。

**参数起点**：插入2帧、4帧、2帧；白闪1帧；腕表Scale从105%到112%跨4帧；V2位置误差控制在圆形直径的5%以内。  
**为什么这样设**：25fps下2帧只有80ms，足以感知但来不及完整阅读；4帧约160ms，能让腕表身份被认出。尺度变化只做7%，既有冲击又不抢走形状匹配。  
**失败症状与修正**：若像PPT轮播，说明每张停太久，先把插入缩短到2–3帧；若像随机闪烁，说明中心没对齐，先关掉所有特效只修Position/Scale；若白闪像视频断了，把1帧改为Opacity `0→100→0`共3帧。  
**迁移思路**：可把“角色—表盘”换成“人眼—相机镜头”或“戒指—咖啡杯口”，关键是共享圆形与中心位置。  
**练习**：找一张人物正面图和一张钟表图，用8–12帧做三次交替，不加任何故障特效。  
**验收**：静音播放仍能感到腕表从角色胸口或头盔中“跳出来”；逐帧检查没有空白帧；切点偏离标记不超过1帧。  
**教程**：[Adobe：无需插件制作Glitch效果](https://www.adobe.com/creativecloud/video/hub/features/add-a-glitch-effect-in-premiere-pro.html)；[Dominic Krupp：PR原生RGB Split](https://www.youtube.com/watch?v=Tdxcit2FetI)（2026-08-06检索约4.4万播放，4:11）  
**能力边界**：PR-native；原片中的具体纹理可能来自预渲染素材。

### T02 角色—腕表—眼部的中心轴匹配

**时间码证据**：00:00:02.400≈帧60为头盔；00:00:02.480≈帧62出现高亮表盘；00:00:02.560≈帧64为带径向模糊的角色；00:00:02.720≈帧68回到腕表；00:00:02.800≈帧70进入眼部特写。见[event-02](evidence/events/event-02-00-00-02-480.jpg)。  
**观察**：头盔、表盘和眼睛均被放在画面中心附近；切换之间有明暗翻转与放射状模糊，但主体方向没有横向跳跃。  
**判断与置信度**：中心轴形状匹配为高置信；径向模糊可能来自源动画或后期模糊，置信度中。  
**原理**：观众在切换时首先追踪“中心在哪里”，其次才读取对象是什么。保持视觉锚点，允许材质和曝光发生很大变化。  
**Premiere 操作**：

1. 将三张素材依次放在V1，每张2–4帧。
2. 在Program Monitor打开安全框或参考线，把头盔中心、表盘轴心和瞳孔都对到同一点。
3. 给腕表和眼睛添加Motion关键帧：切入前Scale 108–115%，落点回到100–105%；关键帧使用Bezier缓入。
4. 若需要软化切口，在切点上方放2–3帧调整图层，使用Directional Blur或Gaussian Blur，从20–35降到0。

**参数起点**：Scale `112%→103%`跨5帧；模糊`25→0`跨3帧；Position只为对齐中心，不做无目的漂移。  
**为什么这样设**：五帧约半拍，观众能看见“到达”而不会觉得慢；模糊只盖住切口，持续太长会让产品失去质感。  
**失败症状与修正**：若切换仍跳，截取切点两侧截图并用50%不透明度叠在一起重新对齐；若画面出现黑边，降低Scale变化或先放大素材；若模糊显得廉价，完全删除模糊检查纯硬切是否已经成立。  
**迁移思路**：任何“中心物体接力”都适用，例如车轮→手表→月亮。  
**练习**：用三个圆形物体做10帧组合，并分别试纯硬切与3帧模糊版。  
**验收**：暂停在切点前后时，三个圆心偏差不超过画面宽度2%；删除模糊后剪辑仍可理解。  
**教程**：[Adobe：Motion中的Position、Scale与Rotation](https://helpx.adobe.com/premiere/desktop/add-video-effects/commonly-used-effects/apply-motion-effect.html)；[Karl Shakur：The PERFECT Match Cut Transition](https://www.youtube.com/watch?v=CWb6ldBOhNE)（2026-08-07检索约108万播放，7:50）；[Justin Odisho：How to do the Match Cut Transition](https://www.youtube.com/watch?v=4DIhLzkYHMA)（约20.7万播放，快照2026-08-07）；[Enam Alamin：3 Cinematic Match Cut Transitions](https://www.youtube.com/watch?v=iLOkHLbHpnY)（约12.3万播放，快照2026-08-07）  
**能力边界**：PR-native；源素材中的真实运动模糊不可由单一参数精确反推。

### T03 头盔眼睛推进到机械虹膜

**时间码证据**：00:00:03.840≈帧96仍是头盔双眼；00:00:03.920≈帧98切到单眼；00:00:04.320≈帧108瞳孔已占据画面中心；00:00:04.560≈帧114开始出现黑色机械片；00:00:04.720≈帧118成为机械虹膜。见[event-03](evidence/events/event-03-00-00-04-200.jpg)。  
**观察**：主体从“头盔中的眼睛”变为“单眼”再变成“机械环”；瞳孔与机械中心基本一致，尺度持续增大，黑色区域逐渐吞没画面。  
**判断与置信度**：形状匹配和连续推近为高置信；机械虹膜的三维展开是源动画，置信度高。  
**原理**：这是“视觉比喻式匹配剪辑”：生物虹膜和机械孔结构相似，持续向中心推进让两个对象看起来属于同一次运动。  
**Premiere 操作**：

1. 先把眼睛与机械环两段素材在V1硬切，确保两侧圆心一致。
2. 给眼睛段Scale做`100%→135%`，持续6–8帧；用Bezier让后半段更快。
3. 机械段从`108%→100%`跨4–6帧落稳，形成“冲进去再停下”的呼吸。
4. 若需要遮住边缘，在V2复制机械段，使用Ellipse Mask从小到大扩张；Mask Feather从8–20px开始。

**参数起点**：眼睛Scale `100→135%/8帧`；机械Scale `108→100%/5帧`；圆心误差小于圆直径5%；遮罩羽化1080p下8–20px。  
**为什么这样设**：八帧能让初学者看清推近；机械段反向回落5帧避免冲击后继续漂移。羽化只处理接缝，不负责掩盖错误对齐。  
**失败症状与修正**：若像两个圆形图片轮播，增强眼睛末端的加速并让机械段从略大的Scale落回；若遮罩有灰边，减少Feather并匹配两层黑位；若机械片看起来是平面旋转，接受源素材限制，不要继续堆PR效果。  
**迁移思路**：眼睛→镜头光圈、地铁隧道→唱片孔、咖啡旋涡→排水口都能使用“中心推进＋圆形比喻”。  
**练习**：用一张眼睛图和一张相机光圈图完成12帧转场，只允许Motion和一个椭圆遮罩。  
**验收**：关掉遮罩后两侧圆心仍对齐；播放时观众先感到“钻入”，再意识到物体改变。  
**教程**：[Adobe：关键帧速度与Bezier图形](https://helpx.adobe.com/premiere/desktop/add-video-effects/control-effects-and-transitions-using-keyframes/edit-keyframes-graphs.html)；[Adobe：形状遮罩](https://helpx.adobe.com/premiere/desktop/add-video-effects/work-with-masks/create-masks-using-shapes.html)；[B站：3种匹配剪辑手法](https://www.bilibili.com/video/BV1vf421f7ra/)（播放量未核实；图形、动作、声音三类思路）  
**能力边界**：PR-approximation；机械几何展开属于3D/source-required。

### T04 HUD扫描人物进入负片故障

**时间码证据**：00:00:06.800≈帧170为多画框HUD人物；00:00:07.360≈帧184开始横向拖影；00:00:07.520≈帧188出现大幅位移；00:00:07.680≈帧192进入高亮负片；00:00:07.920≈帧198仍在白底扫描状态。见[event-04](evidence/events/event-04-00-00-07-400.jpg)。  
**观察**：同一人物被黑白框、文字和准星覆盖；人物边缘出现红青分离；切换前有横向拖影，随后正负片翻转，HUD位置仍保持大体一致。  
**判断与置信度**：RGB错位、HUD合成和正负片插入为高置信；具体位移贴图或插件无法确定，置信度中。  
**原理**：HUD给观众一个稳定“界面层”，底下人物即使被扭曲也不会完全失去方向；RGB错位和短时反相告诉观众这是电子扫描，不是素材损坏。  
**Premiere 操作**：

1. V1放干净人物；Alt拖到V2/V3复制两个3–8帧片段。
2. V2向左移5px并调成红色倾向，V3向右移5px并调成青色倾向；Opacity从0升到50–65%再回0，尝试`Screen`或`Lighten`。
3. 在V4放带Alpha的HUD素材；黑底HUD使用`Screen`，Opacity从35–55%开始。
4. 把故障段切成1–3帧条带，分别改变Position X；在V5调整图层搜索`Invert`，只保留1–2帧。

**参数起点**：RGB水平偏移±5px，持续6帧；复制层Opacity 55%；HUD 45%；故障条带1–3帧；Invert 1–2帧。  
**为什么这样设**：1080宽画面中5px足以出现彩边但不会分裂成三个人；HUD保持低于主体对比；Invert只做标点，不能成为常态。  
**失败症状与修正**：若像廉价彩虹描边，把偏移从10px以上降回3–6px并让效果只在切点出现；若人物看不清，先关HUD再降低复制层Opacity；若画面只是抖动没有方向，把所有故障条带统一为同一横向运动。  
**迁移思路**：HUD可换成相机对焦框、医学扫描、赛车遥测；不变的是“稳定界面＋不稳定主体”。  
**练习**：用一个5秒人物镜头制作8帧故障，限制为三层视频、一个HUD和一个2帧反相。  
**验收**：效果关闭时V1完整；开启时人物身份仍可辨认；RGB彩边只在故障窗口出现；没有意外黑帧。  
**教程**：[Adobe Video × Film Riot：Premiere与AE的Glitch方法](https://www.youtube.com/watch?v=IZb_dZaakYo)；[Justin Odisho：RGB Split Color Glitch Distortion](https://www.youtube.com/watch?v=tBZmONiecyA)（约25.4万播放，快照2026-08-07）；[B站：2分钟RGB数字故障Glitch](https://www.bilibili.com/video/BV157411i7wm/)（约2,900播放，快照2026-08-07，中文快速演示）；[Adobe：混合模式说明](https://helpx.adobe.com/premiere/desktop/add-video-effects/work-with-composites/blend-mode-options.html)  
**能力边界**：PR-approximation；复杂有机位移和精确通道控制为AE-preferred。

### T05 正片—负片—X光线稿的姿态连续

**时间码证据**：00:00:09.840≈帧246为黑底人物；00:00:09.920≈帧248翻成白底负片；00:00:10.160≈帧254回到黑底；00:00:10.720≈帧268再次强反相；00:00:10.800–00:00:10.880≈帧270–272变成白底X光线稿。见[event-05](evidence/events/event-05-00-00-10-400.jpg)。  
**观察**：人物姿势、朝向与胸前圆形装置保持连续，但亮度极性、边缘颜色和纹理不断变化；最后稳定为线稿/X光风格。  
**判断与置信度**：依靠相同姿态的多版本素材做正负片节奏切换，置信度高；X光细节可能是预渲染通道或独立素材，置信度中。  
**原理**：姿态连续提供对象恒常性，亮度翻转提供冲击。观众知道“还是同一个人”，所以能接受画面风格瞬间改变。  
**Premiere 操作**：

1. 将同一姿态的正常版和线稿版对齐放V1/V2；先在无特效状态下对齐肩膀、头顶和胸口圆形。
2. 用Razor切出1–2帧窗口；在窗口上方放调整图层并应用Invert，或直接切换到负片素材。
3. 线稿版使用`Screen`或`Lighten`叠在正常版上，Opacity从60–100%试起；必要时用Lumetri提高对比。
4. 把最终X光版至少稳定4–6帧，让观众有时间读取，不要一直闪。

**参数起点**：反相1帧、正常4–6帧、再反相2帧；线稿Opacity 75%；最终稳定6帧。  
**为什么这样设**：反相是标点，线稿是信息；前者越短越有力，后者必须留出阅读时间。  
**失败症状与修正**：若看起来像播放器颜色坏了，加入明确的声音瞬态和HUD语义；若闪烁太刺眼，减少反相次数并把纯白压到90%以下；若线稿与人物重影，先对齐姿态或只保留线稿，不要用羽化硬救。  
**迁移思路**：产品实拍→工程蓝图、人物→骨骼扫描、建筑→线框模型都能复用“同姿态多渲染通道”。  
**练习**：用一张人物图复制三份，制作正常、黑白高反差、边缘线稿三个版本，按1/5/2/6帧组织。  
**验收**：逐帧看肩膀和头部没有位移；最终风格至少稳定4帧；降低屏幕亮度后仍能辨认主体轮廓。  
**教程**：[Adobe：创建调整图层](https://helpx.adobe.com/premiere/desktop/add-video-effects/apply-video-effects/create-adjustment-layers.html)；[Adobe：设置并动画化Opacity](https://helpx.adobe.com/premiere/desktop/add-video-effects/work-with-composites/specify-clip-opacity.html)  
**能力边界**：PR-native可做反相与合成；高质量X光材质多为AE-preferred或3D/source-required。

### T06 表芯微距穿行到表背英雄镜头

**时间码证据**：00:00:20.800≈帧520开始贴近表芯；00:00:21.200≈帧530沿金属桥移动；00:00:21.680≈帧542仍在微距运动；00:00:21.760≈帧544切到圆形表背；00:00:21.920≈帧548成为侧面完整腕表，00:00:22.000≈帧550在概览中继续稳定。见[event-06](evidence/events/event-06-00-00-21-400.jpg)。  
**观察**：前半段透视、反光和遮挡连续变化，说明相机或3D物体真实移动；切到表背时仍以圆形和黑金材质接力，之后迅速交代完整产品。  
**判断与置信度**：三维微距运镜属于预渲染动画，置信度高；从微距到表背的圆形匹配剪辑为高置信。  
**原理**：先用不可一眼看全的细节制造“探索”，再用完整表体回答“这是什么”。圆形与材质连续让尺度跳变看起来像一次拉远。  
**Premiere 操作**：

1. 选用已经带微距运镜的源视频作为V1前段；PR不负责凭空制造真实齿轮透视。
2. 在00:00:21.76附近找到圆形结构最接近的帧，硬切到表背；用50%叠层检查圆心和金色高光方向。
3. 表背镜头从Scale 112%在5帧内回到100%，并用Position保持圆心；下一镜头完整腕表至少稳定6–10帧。
4. 把金属whoosh或impact放A2，峰值对准硬切，尾音跨到完整产品镜头形成声音桥。

**参数起点**：切点误差±1帧；表背Scale `112→100%/5帧`；完整产品稳定8帧；声音峰值对准帧544。  
**为什么这样设**：5帧约半拍，能把尺度跳跃读成“落稳”；8帧让观众完成产品识别。声音尾巴跨切点会把两个空间粘在一起。  
**失败症状与修正**：若像突然换素材，先对齐圆心和高光运动方向；若数字放大出现假3D，停止继续推Scale，换有真实相机运动的源素材；若完整表体一闪而过，延长英雄镜头而不是继续加特效。  
**迁移思路**：汽车引擎→整车、相机快门→整机、鞋底纹理→整鞋都能使用“细节探索→完整答案”。  
**练习**：用一个微距视频和一个完整产品静帧做12–16帧转场，重点是圆形或高光方向对齐。  
**验收**：暂停在切点两侧能指出同一个视觉锚点；完整产品稳定至少6帧；没有把静态Scale冒充真实3D旋转。  
**教程**：[Adobe：关键帧基础与插值](https://helpx.adobe.com/premiere/desktop/add-video-effects/control-effects-and-transitions-using-keyframes/about-keyframes.html)；[Adobe：转场与素材把手概览](https://helpx.adobe.com/premiere/desktop/add-video-effects/apply-video-transitions/transitions-overview.html)  
**能力边界**：剪辑与落稳为PR-native；微距穿行本身是3D/source-required。

## PR 复刻工程

### 序列与轨道

- 序列：1080×1920、25fps，音频48kHz项目设置也可接受，导入44.1kHz音乐后由PR处理。
- V1：连续的主3D/人物/产品镜头。
- V2–V3：2–8帧插入、RGB复制层、线稿版本。
- V4：HUD和扫描图形。
- V5：短调整图层，负责Invert、统一模糊或短时调色。
- V6：白色Color Matte，仅用于1–3帧闪光。
- A1：音乐；A2：impact/whoosh；A3：机械细节声。

### 建议搭建顺序

1. **结构剪辑**：只用V1和A1完成30秒的镜头顺序，按252.1 BPM候选打标记（若你听到的节奏明显不同，以你的听感为准，改标记即可）。
2. **关键帧与节奏**：完成圆心对齐、Scale落稳和2–4帧插入；此时不要加HUD。
3. **合成与遮罩**：加入RGB复制层、线稿、HUD和必要遮罩；每加一层都要能单独关闭。
4. **调色与声音**：统一黑白金，最后加反相、白闪、impact和whoosh。

## 分层练习

### 10分钟：单一原则

用眼睛和钟表两张图片完成T03的12帧版本。只允许Motion和一个Ellipse Mask。验收：圆心偏差小于画面宽度2%，关掉遮罩仍能看懂匹配关系。

### 30分钟：完整转场

使用一个人物片段制作T04：V1干净人物，V2/V3红青错位，V4 HUD，V5两帧Invert。验收：关闭V2–V5后V1完整；故障窗口不超过8帧；RGB偏移不持续驻留。

### 迁移挑战

禁止使用角色和腕表。改用“人眼—相机镜头—城市隧道”制作20秒版本，保留圆形匹配、半拍插帧和“稳定界面＋不稳定主体”，但重新设计颜色与HUD。

## 自测与交作业

- [ ] 切点与标记误差不超过1帧。
- [ ] 每个效果都能指出before、mechanism、after三个状态。
- [ ] 转场后在下一强拍前稳定。
- [ ] 关闭特效层后基础剪辑仍成立。
- [ ] 没有黑边、遮罩灰边或无意跳帧。
- [ ] 能用自己的话解释“为什么匹配形状比堆插件更重要”。
- [ ] 能指出至少一处必须依赖3D源素材的画面。

## 教程链接

建议按这个顺序学习：

1. [Adobe：关键帧是什么](https://helpx.adobe.com/premiere/desktop/add-video-effects/control-effects-and-transitions-using-keyframes/about-keyframes.html)
2. [Adobe：添加关键帧](https://helpx.adobe.com/premiere/desktop/add-video-effects/control-effects-and-transitions-using-keyframes/add-keyframes.html)
3. [Adobe Video：Keyframes与Velocity演示](https://www.youtube.com/watch?v=CmVwG-kv6jo)
4. [Adobe：Motion控制Position、Scale、Rotation](https://helpx.adobe.com/premiere/desktop/add-video-effects/commonly-used-effects/apply-motion-effect.html)
5. [Adobe：形状遮罩](https://helpx.adobe.com/premiere/desktop/add-video-effects/work-with-masks/create-masks-using-shapes.html)
6. [Adobe：混合模式](https://helpx.adobe.com/premiere/desktop/add-video-effects/work-with-composites/blend-mode-options.html)
7. [Adobe：无需插件制作Glitch](https://www.adobe.com/creativecloud/video/hub/features/add-a-glitch-effect-in-premiere-pro.html)
8. [Adobe：Time Remapping与速度渐变](https://helpx.adobe.com/premiere/desktop/edit-projects/change-clip-speed/change-clip-speed-and-duration-using-time-remapping.html)
9. [YouTube：The PERFECT Match Cut Transition](https://www.youtube.com/watch?v=CWb6ldBOhNE)（约108万播放，数据快照2026-08-07）
10. [YouTube：PR原生RGB Split](https://www.youtube.com/watch?v=Tdxcit2FetI)（约4.4万播放，数据快照2026-08-06）
11. [B站：利用PR时间重映射打造变速剪辑](https://www.bilibili.com/video/BV1MS4y1r7Am/)（约11.7万播放，数据快照2026-08-06；作为拓展练习，本样片不据此断言存在速度重映射）
12. [B站：3种匹配剪辑手法](https://www.bilibili.com/video/BV1vf421f7ra/)（播放量未核实，数据快照2026-08-06）
13. [B站：视频变速 时间重映射“神奇的变速齿轮”（PR2024 基础教程）](https://www.bilibili.com/video/BV1xz421e7MU/)（约4,000播放，数据快照2026-08-07）
14. [B站：第十八节 视频变速—时间重映射（PR2025 新版快速上手）](https://www.bilibili.com/video/BV1UF7mzzEtY/)（约3,600播放，数据快照2026-08-07）

### 推荐教程视频（2026-08-07 检索快照）

以下为教程检索快照（`tutorial-research-auto/tutorial-research.md`）的推荐项，按主题分组；播放量为快照当日数据，使用前请打开确认其确实演示了对应技法。

**匹配剪辑（match cut）**

- [YouTube：The PERFECT Match Cut Transition（Karl Shakur）](https://www.youtube.com/watch?v=CWb6ldBOhNE)（约108万播放，7:50）
- [YouTube：How to do the Match Cut Transition（Justin Odisho）](https://www.youtube.com/watch?v=4DIhLzkYHMA)（约20.7万播放，4:13）
- [YouTube：3 Cinematic Match Cut Transitions（Enam Alamin）](https://www.youtube.com/watch?v=iLOkHLbHpnY)（约12.3万播放，5:05）
- [B站：快速剪辑-插入（转场合集，含形状/遮挡物转场）](https://www.bilibili.com/video/BV1RM4y1W7iY/)（约1.5万播放，1:26）
- [B站：PR/AE特效转场系统课](https://www.bilibili.com/video/BV1kyuc6eEFZ/)（约2,800播放）
- [B站：混剪卡点教程（含匹配剪辑手法）](https://www.bilibili.com/video/BV1ahiuecEZT/)（约2,400播放，4:57）

**RGB 故障 / 错位（rgb-glitch）**

- [YouTube：How to Create RGB Split Color Glitch Distortion（Justin Odisho）](https://www.youtube.com/watch?v=tBZmONiecyA)（约25.4万播放，4:32）
- [YouTube：PR原生RGB Split（Dominic Krupp）](https://www.youtube.com/watch?v=Tdxcit2FetI)（约4.4万播放，4:11）
- [YouTube：EASY RGB Split/Glitch EFFECT（Ranai R）](https://www.youtube.com/watch?v=QaXQKzz_IWg)（180播放，2:37）
- [B站：2分钟学会RGB数字故障特效Glitch（无需插件）](https://www.bilibili.com/video/BV157411i7wm/)（约2,900播放，6:34）
- [B站：3分钟教你实现Glitch数字故障转场效果](https://www.bilibili.com/video/BV1Ej411T73M/)（约1.3万播放，3:51）

**速度重映射（speed ramp）**

- [YouTube：PR Tutorial｜时间重映射 Speed Ramping（黄豆Bean）](https://www.youtube.com/watch?v=ctyQKmYf8XU)（约1.9万播放，11:05）
- [YouTube：3分钟轻松实现视频的变速（卡敏与阿超）](https://www.youtube.com/watch?v=6-oazg_AMEE)（639播放，2:54）
- [B站：PR时间重映射教程·利用关键帧做速度转场](https://www.bilibili.com/video/av83387437/)（约4,700播放，2:38）
- [B站：视频变速 时间重映射“神奇的变速齿轮”（PR2024）](https://www.bilibili.com/video/BV1xz421e7MU/)（约4,000播放，2:30）
- [B站：第十八节 视频变速—时间重映射（PR2025 新版快速上手）](https://www.bilibili.com/video/BV1UF7mzzEtY/)（约3,600播放，2:30）

速度重映射在本样片中是拓展练习：成片证据未断言存在速度重映射，学习变速技法的链接列在上方仅供自主练习。

## 能力边界

- 可以从成片高置信识别形状匹配、插帧长度、亮度翻转、RGB边缘、HUD叠层和节奏关系。
- 无法仅凭导出片确定原作者使用的插件、预设、轨道结构或精确参数；本课参数是PR复刻起点。
- 机械虹膜、腕表内部穿行、真实反射和透视旋转明显依赖3D或预渲染源素材。PR负责选择、定时、合成和声音，不应被描述成“一键3D特效”。
- 若要把6个事件升级为每一源帧检查，可用forensic模式；视觉证据和token消耗都会显著上升。

> 闪烁安全：本片多次出现1–2帧高反差正负片和白闪。学习时降低预览亮度、避免循环长时间观看；公开作品应减少连续闪烁频率和次数，并为光敏观众考虑更柔和版本。
