import streamlit as st
import openai
import hashlib
import os
import time

# 在 st.session_state 里存缓存
if "tactic_cache" not in st.session_state:
    st.session_state.tactic_cache = {}

# ===== 调试模式：跳过 API Key 检查 =====
DEBUG_MODE = False  # 正式上线时改成 False

from openai import OpenAI

if DEBUG_MODE:
    client = OpenAI(api_key="debug-mode-no-api-needed", base_url="https://api.deepseek.com")
else:
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        st.sidebar.markdown("---")
        api_key_input = st.sidebar.text_input(
            "🔑 DeepSeek API Key",
            type="password",
            placeholder="sk-...",
            help="输入后自动生效，不会保存"
        )
        if api_key_input:
            api_key = api_key_input
    if not api_key:
        st.warning("⚠️ 请输入 DeepSeek API Key")
        st.stop()
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
# ===== 结束 =====

st.set_page_config(page_title="腰旗战术官 | FLAG TACTICS MANAGER", page_icon="🏈")
# ... 后续代码不变
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
# ==================== 54条战术完整库 ====================
tactics_full = [
    {
        "name": "飞驰路线 (Fly Route)",
        "desc": "C开球后原地保护，QB接球后三步后撤观察，左侧WR全速垂直冲刺30码以上直接攻击对方安全卫身后纵深，右侧WR跑中距离回身路线牵制同侧角卫，Slot从槽位释放后跑浅区横穿清理坪区防守者。\n(C protects in place after snap. QB takes a 3-step drop and reads the field. Left WR sprints vertically 30+ yards to attack the space behind the safety. Right WR runs an intermediate hitch to occupy the corner. Slot releases from the slot and runs a shallow cross to clear the flat defender.)",
        "标签": ["速度慢", "防守前压(Blitz)"]
    },
    {
        "name": "回身路线 (Hitch Route)",
        "desc": "C开球后向前推挡一步后滞留中路，QB三步后撤快速阅读，左侧WR冲刺8码后急停转身回跑2码面向QB，右侧WR跑3码斜插带走同侧防守者，Slot和RB分别向两侧坪区释放提供快速出球选择。\n(C takes one step forward to block then holds in the middle. QB drops back 3 steps and reads quickly. Left WR sprints 8 yards, stops abruptly, turns back 2 yards to face QB. Right WR runs a 3-yard slant to pull the defender away. Slot and RB release to opposite flats to provide quick outlet options.)",
        "标签": ["急停防弱", "跟防惯性大(Poor Stop Ability)"]
    },
    {
        "name": "斜插路线 (Slant Route)",
        "desc": "C开球后向左前方推挡协助保护口袋左侧，QB接球后两步后撤快速出球，槽位Slot向外侧虚晃一步后立刻以45度角斜插切入场地中央纵深，左侧WR沿边线垂直冲深吸引角卫远离中路，右侧WR跑5码Out路线将同侧防守者带向边线，RB留在后场做最后一道阻挡。\n(C blocks to the left front to protect the pocket's left side. QB takes a 2-step drop and releases quickly. Slot fakes outside then immediately cuts inside at a 45-degree angle into the middle of the field. Left WR runs a vertical route along the sideline to pull the corner away from the middle. Right WR runs a 5-yard Out to take his defender to the boundary. RB stays in the backfield for final protection.)",
        "标签": ["外站位", "内侧变向慢(Slow Inside Reaction)"]
    },
    {
        "name": "外侧直角路线 (Out Route)",
        "desc": "C开球后向右推挡保护口袋右侧，QB三步后撤将球快速传向边线，右侧WR直线冲刺7码后以90度直角突然切向边线方向，左侧WR跑Post路线牵制安全卫留在中路深处，Slot跑3码斜插分散线卫注意力，RB释放到右坪区提供安全阀。\n(C blocks right to protect the right side of the pocket. QB takes a 3-step drop and passes quickly to the boundary. Right WR sprints 7 yards straight then makes a sharp 90-degree cut toward the sideline. Left WR runs a Post to hold the safety deep in the middle. Slot runs a 3-yard slant to distract the linebacker. RB releases to the right flat as a safety valve.)",
        "标签": ["重心偏内", "外侧变向弱(Poor Outside Reaction)"]
    },
    {
        "name": "内侧直角路线 (In Route)",
        "desc": "C开球后居中保护，QB接球后快速阅读线卫位置，槽位Slot直线冲刺5码后以90度直角切入场地中央抢中线空间，左侧WR沿边线冲刺8码跑Curl路线牵制同侧角卫无法内收协防，右侧WR跑Corner路线清空边路纵深的潜在协防者，RB从后场释放到左坪区。\n(C blocks in the center. QB receives the snap and reads the linebacker position quickly. Slot sprints 5 yards then cuts 90 degrees into the middle of the field to claim central space. Left WR runs 8 yards up the sideline on a Curl to prevent his corner from helping inside. Right WR runs a Corner route to clear deep coverage on that side. RB releases from the backfield to the left flat.)",
        "标签": ["面向外侧", "转身内切慢(Slow Cut Inside)"]
    },
    {
        "name": "柱状路线 (Post Route)",
        "desc": "C开球后保护中路防止突击，QB五步后撤等待深远路线展开，左侧WR加速冲刺12码后以45度角切入场地中央深处指向球门立柱方向，右侧WR同样跑Post路线从另一侧向中央汇集形成双柱夹击安全卫的态势，Slot跑短斜插占据线卫眼前制造中短距离威胁，RB留在后场阻挡任何漏进来的突击者。\n(C blocks the middle to prevent a blitz. QB takes a 5-step drop to wait for deep routes to develop. Left WR accelerates 12 yards then cuts at a 45-degree angle toward the center goalpost. Right WR runs the same Post route from the other side, creating a dual-post attack that squeezes the safety. Slot runs a short slant to occupy the linebacker and create a mid-range threat. RB stays in the backfield to block any leaking rushers.)",
        "标签": ["中路纵深空", "安全卫外扩(Poor Safety Coverage)"]
    },
    {
        "name": "底角路线 (Corner Route)",
        "desc": "C开球后向右推挡协助强侧保护，QB五步后撤将球导向边线底角，右侧WR全速冲刺10码后以45度角切向边线和底线交汇的底角区域，左侧WR跑Post路线将安全卫吸引在中路深处使其无法回补边角，Slot跑5码Hitch路线牵制槽角卫不敢后退过深，RB释放到右坪区预防QB受压时快速出球。\n(C blocks right to protect the strong side. QB takes a 5-step drop and guides the ball toward the boundary corner of the end zone. Right WR sprints 10 yards then cuts at a 45-degree angle toward the corner where the sideline meets the end line. Left WR runs a Post to pull the safety deep in the middle, preventing him from helping on the corner. Slot runs a 5-yard Hitch to freeze the slot corner from dropping too deep. RB releases to the right flat for a quick outlet if QB is pressured.)",
        "标签": ["边路纵深空", "角卫压上(Poor Corner Coverage)"]
    },
    {
        "name": "柱角假动作路线 (Post-Corner Route)",
        "desc": "C开球后掩护中路面并观察有无突击，QB七步深撤等待双变向完成，槽位Slot先向内侧做一个Post假动作诱使安全卫向前压上补位，紧接着猛然二次变向切向外侧底角全速冲刺，左侧WR跑Corner路线从另一侧牵制对位角卫，右侧WR跑Dig切入中路埋伏在中区防线的缝隙中，RB在Slot启动二次变向时快速释放到同侧坪区。\n(C blocks the middle and watches for blitzers. QB takes a 7-step deep drop to let the double move develop. Slot first fakes a Post route inside, baiting the safety to step forward and cover, then immediately makes a second cut toward the outside corner at full speed. Left WR runs a Corner route to occupy his corner from the other side. Right WR runs a Dig into the middle, hiding in the seams of the zone. RB releases to the flat on the same side when Slot makes his second cut.)",
        "标签": ["预判被骗", "二次变向失位  (Poor Double Move Execution)"]
    },
    {
        "name": "角柱假动作路线 (Corner-Post Route)",
        "desc": "C开球后保护口袋注意两侧边缘冲击，QB五步后撤后耐心等待路线发展，右侧WR先向外做一个Corner假动作诱使角卫全力保护边线，待防守者身体重心外移后突然二次变向以45度角切回球场中央深区，左侧WR跑Fly路线将安全卫钉在另一侧纵深使其无法横移补位，Slot跑In路线从另一侧切入中央形成中路多层接应点，RB留在后场保护。\n(C blocks the pocket, watching for edge pressure on both sides. QB takes a 5-step drop and waits for the route to develop. Right WR first fakes a Corner route outside, baiting the corner to fully commit to protecting the sideline. Once the defender shifts his weight outside, WR makes a second cut at a 45-degree angle back toward the deep middle. Left WR runs a Fly to pin the safety on the other side, preventing him from sliding over. Slot runs an In route from the other side to create multiple layers in the middle. RB stays in the backfield for protection.)",
        "标签": ["外侧保护过度", "内线空虚  (Poor Edge Protection)"]
    },
    {
        "name": "急停再启动路线 (Stop and Go Route)",
        "desc": "C开球后推挡保护并注意是否有线卫延迟突击，QB五步后撤后先假动作骗防守者以为要短传，左侧WR全速冲刺约9码后急停做回身状，诱使对位角卫也急停准备扑前断球，待防守者被冻结后左侧WR不等其反应立即二次全速冲刺纵深，右侧WR跑Hitch路线提供中距离安全阀门，Slot跑浅横穿清理中路短区，RB在右侧WR回身时向其方向释放。\n(C blocks and watches for delayed linebacker blitz. QB drops back 5 steps and uses a pump fake to sell a short pass. Left WR sprints about 9 yards, stops abruptly, and turns back as if receiving a hitch, baiting the corner to stop and jump the route. Once the defender is frozen, Left WR immediately accelerates again at full speed deep. Right WR runs a Hitch to provide a mid-range safety valve. Slot runs a shallow cross to clear the short middle. RB releases toward Right WR when he turns back.)",
        "标签": ["启动加速慢", "惯性冻结   (Poor Acceleration)"]
    },
    {
        "name": "座椅路线 (Chair Route)",
        "desc": "C开球后向左推挡建立口袋边缘保护，QB五步后撤观察左侧发展，左侧WR向前跑4码后横向平移切向边线，紧接着沿边线方向垂直冲刺底线，对位角卫在横向平移时被迫转髋跟防，二次垂直变向时身体平衡被完全打乱，右侧WR跑Dig路线深入中场吸引安全卫，Slot跑Slant切入中央占线卫视野，RB在左侧WR横向移动时向左侧坪区释放。\n(C blocks left to set the edge of the pocket. QB takes a 5-step drop and watches the left side develop. Left WR runs forward 4 yards, then laterally toward the sideline, followed by a vertical sprint down the boundary. The corner is forced to flip his hips during the lateral movement and loses balance during the second vertical cut. Right WR runs a Dig deep in the middle to draw the safety. Slot runs a Slant into the center to occupy the linebacker. RB releases to the left flat when Left WR makes his lateral move.)",
        "标签": ["横向平衡差", "连续变向弱(Poor Lateral Balance and Cuts)"]
    },
    {
        "name": "选项路线 (Option Route)",
        "desc": "C开球后居中保护并观察防守阵型，QB三步后撤快速阅读槽位的对位防守者站位，槽位Slot先做一个斜插状假动作诱惑防守者反应，若防守者明显防内则立刻改为沿外侧平行线跑向边线方向，若防守者防外则保持斜插切入中央，左侧WR跑Corner路线牵制同侧角卫，右侧WR跑Fly路线清空另一侧纵深安全卫，RB从后场直接释放到Slot同侧的坪区做第二选项。\n(C blocks in the center and reads the defensive formation. QB takes a 3-step drop and quickly reads the slot defender's positioning. Slot fakes a Slant to bait a reaction. If the defender protects inside, Slot immediately changes to a flat route along the sideline. If the defender protects outside, Slot continues the Slant inside. Left WR runs a Corner to occupy that side's corner. Right WR runs a Fly to clear the safety on the other side. RB releases directly to the flat on the same side as Slot as a second option.)",
        "标签": ["阅读犹豫", "选项防判断差(Poor Option Reading and Execution)"]
    },
    {
        "name": "卷曲路线 (Curl Route)",
        "desc": "C开球后向强侧推挡建立稳固口袋，QB五步后撤将球准确投向边线区域，强侧WR冲刺约10码后在边线处划出一条小圆弧回身向外寻球，利用防守者因忌惮深球而后退过深造成的空间差接球，弱侧WR跑Post路线将安全卫钉在中路深处，Slot跑In路线从中路插入占据任何试图外补的线卫，RB释放到强侧坪区做应急出球点。\n(C blocks to the strong side to establish a solid pocket. QB takes a 5-step drop and delivers the ball accurately to the boundary. The strong-side WR sprints about 10 yards, then runs a small arc back toward the sideline to look for the ball, exploiting the space created by the defender who is bailing too deep in fear of a deep pass. Weak-side WR runs a Post to pin the safety deep in the middle. Slot runs an In route into the middle to occupy any linebacker trying to help outside. RB releases to the strong-side flat as an emergency outlet.)",
        "标签": ["后退过深", "包夹回追慢 (Poor Deep Coverage and Pursuit)"]
    },
    {
        "name": "回退长路线 (Comeback Route)",
        "desc": "C开球后全力保护口袋并注意延迟突击，QB七步深撤等待深远路线充分展开，左侧WR全力冲刺15码以上深区迫使对位角卫转身全速追跑，随后WR用一道圆弧轨迹折返向启球线方向回退约4码，防守者在全速后退中无法同步急停再前移导致完全脱离覆盖，右侧WR跑Fly将安全卫拖离此侧，Slot跑浅区Hitch牵制槽角卫，RB释放到左侧坪区。\n(C fully commits to pocket protection and watches for delayed blitz. QB takes a 7-step deep drop to let the deep route fully develop. Left WR sprints 15+ yards deep to force the corner to turn and run at full speed, then uses an arc trajectory to come back about 4 yards toward the line of scrimmage. The defender, running at full speed backward, cannot stop and come forward simultaneously, losing coverage completely. Right WR runs a Fly to drag the safety away from this side. Slot runs a shallow Hitch to occupy the slot corner. RB releases to the left flat.)",
        "标签": ["转身急停差", "深区回追控制弱(Poor Deep Coverage and Pursuit)"]
    },
    {
        "name": "鞭打路线 (Whip Route)",
        "desc": "C开球后向右推挡注意外侧冲击，QB三步后撤观察区域防守的交接瞬间，槽位Slot先向内侧做一个虚晃斜插动作做出要接中路短传的样子，诱使对位防区和中路防区的防守者交接出现一瞬间迟疑，随即Slot猛然切向外侧跑平路线如同鞭梢甩出，左侧WR跑Corner路线截住边线纵深，右侧WR跑5码In路线占据中央，RB释放到槽位同侧坪区。\n(C blocks right, watching for outside pressure. QB takes a 3-step drop and reads the zone handoff moment. Slot first fakes a Slant inside, appearing to receive a short pass in the middle, creating a momentary hesitation in the zone handoff between defenders. Slot then snaps sharply to the outside on a flat route like a whip cracking. Left WR runs a Corner to control the deep boundary. Right WR runs a 5-yard In route to occupy the middle. RB releases to the flat on the same side as Slot.)",
        "标签": ["区域交接模糊", "犹豫缝隙( Poor Zone Handoff and Hesitation)"]
    },
    {
        "name": "深凿路线 (Dig Route)",
        "desc": "C开球后居中保护并帮助双A缝防突击，QB五步后撤等待中央路线展开，槽位Slot垂直冲刺12码后以接近90度的直角猛然切入场地中央心脏地带，利用两个防守区域横向补位节奏不同步的瞬间在夹层中接球，左侧WR跑Corner路线清空左侧纵深使安全卫向左偏移，右侧WR跑Hitch路线在短距离提供快出选择，RB在Slot切入中央时同步向反方向坪区释放。\n(C blocks in the middle and helps both A-gaps against blitz. QB takes a 5-step drop and waits for the middle route to develop. Slot sprints vertically 12 yards, then cuts sharply at nearly a 90-degree angle into the heart of the field, catching the ball in the seam between two zones whose lateral coverage is out of sync. Left WR runs a Corner to clear deep on the left, pulling the safety that way. Right WR runs a Hitch to provide a quick short option. RB releases to the flat on the opposite side when Slot cuts inside.)",
        "标签": ["横移补位慢", "区域夹层(Poor Zone Coverage in the Middle)"]
    },
    {
        "name": "高弧深远路线 (Fade Route)",
        "desc": "C开球后全力保护口袋为深球争取时间，QB五步后撤后将球高弧度抛向端区角落，左侧大外接WR直接冲向边线底角端区，利用身高弹跳优势在1对1高空球争夺中获得优势，右侧WR跑Post路线将安全卫拉向中路深处避免其回防补位，Slot跑Slant切入中低区域清空线卫视线，RB留在后场阻挡任何冲破口袋的防守者。\n(C fully protects the pocket to buy time for the deep throw. QB takes a 5-step drop and arcs the ball high toward the corner of the end zone. Left outside WR sprints directly to the boundary corner of the end zone, using height and jumping advantage to win the 50-50 ball. Right WR runs a Post to pull the safety deep into the middle, preventing him from rotating back. Slot runs a Slant into the intermediate area to clear the linebacker's vision. RB stays in the backfield to block any defender who breaks through.)",
        "标签": ["身高弹跳弱", "争顶劣势(Poor Jumping Ability)"]
    },
    {
        "name": "坪区路线 (Flat Route)",
        "desc": "C开球后向前推挡后立即释放转身跑向启球线附近的边路坪区成为第六个接球选项，QB两步后撤快速将球传到坪区，左侧WR跑Fly路线全速冲深将同侧角卫和安全卫注意力全部拖入纵深，右侧WR跑Corner路线清空另一侧边路纵深，Slot跑In路线挤入中央占据线卫视野，整个防守被深远路线拉空后的坪区完全无人看守。\n(C blocks forward briefly then immediately releases and turns toward the boundary flat near the line of scrimmage, becoming the sixth receiving option. QB takes a 2-step drop and quickly passes to the flat. Left WR runs a Fly at full speed to drag the corner and safety deep on that side. Right WR runs a Corner to clear the other sideline deep. Slot runs an In route into the middle to occupy the linebacker's vision. The entire defense is stretched by deep routes, leaving the flat completely unguarded.)",
        "标签": ["坪区真空", "深区牵制过深(Poor Deep Coverage)"]
    },
    {
        "name": "车轮路线 (Wheel Route)",
        "desc": "RB从后场启动先向边线方向横向跑动做出要接坪区短传的样子，诱使对位线卫也横向移动准备防守短传，随即RB突然转为垂直冲刺全速沿边线冲向纵深，线卫在横向移动中被迫转身追跑由于绝对速度和转身能力不足被迅速甩开，C开球后保护后释放到反方向坪区，左侧WR跑Post路线牵制安全卫，右侧WR跑Curl路线在边线短距离埋伏，Slot跑In路线占据中路。\n(RB starts from the backfield by running laterally toward the sideline as if receiving a flat pass, baiting the linebacker to move laterally to defend the short throw. RB then suddenly turns vertically and sprints at full speed along the sideline deep. The linebacker, already in lateral motion, is forced to turn and chase but is quickly outrun due to lack of speed and turn ability. C blocks then releases to the opposite flat. Left WR runs a Post to occupy the safety. Right WR runs a Curl to set up on the boundary. Slot runs an In route into the middle.)",
        "标签": ["转身追跑慢", "坪区防深弱(Poor Flat Coverage)"]
    },
    {
        "name": "拖拽横穿路线 (Drag Route)",
        "desc": "C开球后居中保护两步后释放到右侧坪区，QB三步后撤寻找横穿目标，槽位Slot从左侧启动以中等速度贴启球线横穿全场跑向右侧，利用沿途左侧WR跑Fly清空左侧、右侧WR跑In路线占据中央、RB在中间位置做假阻挡等队友的路线和身体作为流动掩护，盯人防守者在追逐中被反复阻延导致Slot在无人紧贴的情况下接球转身获得推进空间。\n(C blocks in the middle for two counts then releases to the right flat. QB takes a 3-step drop and looks for the crossing target. Slot launches from the left side at moderate speed, running a Drag route just above the line of scrimmage across the entire field toward the right. Using teammates as moving picks—Left WR clears with a Fly, Right WR occupies the middle with an In, RB fakes a block in the middle—man defenders are repeatedly obstructed during pursuit. Slot catches the ball with no one tight on him, turns, and gains yards after catch.)",
        "标签": ["盯人挂挡", "掩护摆脱盲区(Poor Blocking and Coverage)"]
    },
    {
        "name": "单后场阵型战术1 (Single Back Play 1)",
        "desc": "I字阵型站位，C开球后向前推挡后即释放走Corner路线沿边线攻击中深区域，QB五步后撤阅读防守层次分布，左侧WR跑Fly路线全速冲深将整条左侧防线拖入纵深，右侧WR跑Slant路线从右外侧45度切向中央短区域吸引线卫注意，RB从单后场位置先做假阻挡动作延误突击者随后走坪区路线到右侧提供安全阀。防守方在同时面对深、中、短三层路线时内部分工混乱导致必然漏掉一人。\n(I-formation alignment. C blocks forward then releases on a Corner route along the sideline to attack the intermediate-deep area. QB takes a 5-step drop and reads the defensive layers. Left WR runs a Fly at full speed, dragging the entire left defense deep. Right WR runs a Slant from the right outside at a 45-degree angle into the short middle to draw linebacker attention. RB from the single-back position first fakes a block to delay blitzers, then releases to the right flat as a safety valve. The defense, facing deep, intermediate, and short routes simultaneously, gets confused in coverage assignments and inevitably leaves someone open.)",
        "标签": ["多层路线混乱", "分工不清( Poor Coverage Assignments)"]
    },
    {
        "name": "单后场阵型战术2 (Single Back Play 2)",
        "desc": "I字阵型站位，C开球后全力保护口袋，QB五步深撤让路线充分发展，左右两侧WR同时跑Post路线从两翼向中央深处汇集形成双柱夹击态势迫使安全卫必须在两人间做选择，槽位WR从内线释放后跑Corner路线攻击被安全卫放弃的边路纵深空间，RB在开球后做假阻挡留在后场保护，待安全卫做出选择后QB将球传向安全卫无法覆盖的一侧。\n(I-formation alignment. C fully protects the pocket. QB takes a 5-step deep drop to let routes fully develop. Both outside WRs run Post routes from opposite wings converging toward the deep middle, creating a dual-post squeeze that forces the safety to choose between them. The slot WR releases from the inside and runs a Corner route to attack the boundary deep area that the safety has abandoned. RB fakes a block after the snap and stays for protection. Once the safety commits, QB throws to the side the safety cannot cover.)",
        "标签": ["安全卫协防弱", "边路单挑(Poor Boundary Play)"]
    },
    {
        "name": "单后场交叉路线 (Single-Back Criss-Cross)",
        "desc": "I字阵型站位，C开球后保护后释放跑Slant路线从中间偏左斜切中央，左侧WR跑反向Slant与C的路线形成交叉态势，两人的路线在启球线5码处交错通过使防守者被迫相互绕行被挂住，右侧WR跑In路线切入中央深处占据安全卫前方空间，RB从单后场走Out路线到右侧边线短区，远端Slot跑浅横穿到左侧坪区，区域防守在横向上被多个交叉路线撕扯导致两个防区之间出现真空。\n(I-formation alignment. C blocks then releases on a Slant from the middle-left into the center. Left WR runs a reverse Slant, creating a criss-cross with C at 5 yards past the line of scrimmage. Defenders are forced to navigate around each other and get rubbed off. Right WR runs an In route deep into the middle, occupying the space in front of the safety. RB from the single-back runs an Out route to the right flat. The far Slot runs a shallow cross to the left flat. Zone coverage is torn horizontally by multiple crossing routes, creating a vacuum between two zones.)",
        "标签": ["区域横移慢", "交叉空档    (Poor Zone Lateral Movement and Crossing Routes)"]
    },
    {
        "name": "分散阵型战术1 (Spread Play 1)",
        "desc": "四人全分散站位，C开球后向后保护口袋，QB三步后撤快速判断防守弱者所在位置，左侧WR跑Fly路线全力冲深压迫同侧角卫和安全卫后退保护身后，右侧WR跑Option路线根据防守者站位自主选择内侧斜插或外侧平跑使对位防守者陷入犹豫，槽位Slot从中路位置跑斜插补足内线短传空间，RB从后场释放到右侧坪区提供快速出球点。防守在全场被拉开的宽度下横向延展不足导致弱侧补防永远慢半拍。\n(Four-wide fully spread formation. C blocks backward to protect the pocket. QB takes a 3-step drop and quickly identifies the defensive weakness. Left WR runs a Fly at full speed, pressing the corner and safety to retreat and protect deep. Right WR runs an Option route, choosing inside slant or outside flat depending on the defender's positioning, making the defender hesitate. Slot from the middle runs a Slant to fill the short inside space. RB releases from the backfield to the right flat for a quick outlet. The defense, stretched across the full width of the field, lacks horizontal range and weak-side help always arrives a step late.)",
        "标签": ["横向延展差", "弱侧补防慢(Poor Weak Side Help)"]
    },
    {
        "name": "分散阵型战术2 (Spread Play 2)",
        "desc": "四人全分散站位，C开球后向右推挡保护强侧，QB五步后撤后将球分配向防守衔接最薄弱的层级，左侧WR跑Corner路线攻击边线纵深，槽位Slot跑In路线从槽位切入中央中距离区域，右侧WR跑Out路线切向边线短区域，RB留在后场做阻挡后延迟释放到左坪区。三层路线从前到后全面覆盖防守区域，而防守方的区域划分过于死板导致两个防区衔接处完全无人盯防。\n(Four-wide fully spread formation. C blocks right to protect the strong side. QB takes a 5-step drop and distributes the ball to the weakest layer of the defense. Left WR runs a Corner to attack the boundary deep. Slot runs an In route from the slot into the intermediate middle. Right WR runs an Out route toward the boundary short area. RB stays in the backfield to block, then releases late to the left flat. Three layers of routes—deep, intermediate, short—fully cover the defense. The defense's rigid zone assignments leave the seams between two zones completely uncovered.)",
        "标签": ["区域衔接差", "分层漏洞(Poor Zone Seam Coverage)"]
    },
    {
        "name": "分散阵型战术3 (Spread Play 3)",
        "desc": "四人全分散站位，C开球后居中保护，QB快速两步后撤在2秒内出球，左侧WR和槽位Slot在左侧短区域做Out和Slant交叉跑动，两人在5码范围内交错通过故意制造防守者的互相推挤和挂挡，右侧WR跑3码Hitch提供第二选项，RB从后场释放到左侧坪区预备接球。人盯人防守者跟防交叉路线时因不会绕过掩护而互相碰撞导致至少一人完全空出。\n(Four-wide fully spread formation. C blocks in the middle. QB takes a quick 2-step drop and releases within 2 seconds. Left WR and Slot on the left side run Out and Slant routes that cross within a 5-yard area, deliberately creating a rub/pick situation where defenders collide with each other. Right WR runs a 3-yard Hitch to provide a second option. RB releases from the backfield to the left flat as a ready receiver. Man defenders following the crossing routes don't know how to navigate the natural pick and collide, leaving at least one receiver completely free.)",
        "标签": ["盯人互挂", "短距交叉漏(Poor Short-Distance Crossing Coverage)"]
    },
    {
        "name": "右侧三叉戟阵型 (Trips Right)",
        "desc": "三名接球手全部紧密排列在右侧，C开球后向左推挡迷惑防守后释放到空旷的左侧短区，QB两步后撤快速判断防守重心偏移情况，右侧最外侧WR跑Fly路线全速冲深钉住角卫和安全卫，中间WR跑Corner路线占据右侧中深度边线区域，内侧槽位跑Out路线切向右侧边线短区，左侧仅剩的一名WR跑Slant切入中央。防守将绝大部分人员调往强侧后左侧已完全处于人数劣势。\n(Three receivers all tightly aligned on the right. C blocks left to deceive the defense, then releases to the wide-open left short area. QB takes a 2-step drop and quickly reads the defensive shift. The rightmost WR runs a Fly at full speed, pinning the corner and safety deep. The middle WR runs a Corner to occupy the intermediate-deep boundary on the right. The inside slot runs an Out toward the right flat. The lone left WR runs a Slant into the middle. After the defense shifts most defenders to the strong side, the left side is completely outnumbered.)",
        "标签": ["弱侧弃守", "兵力偏侧(Poor Weak Side Coverage)"]
    },
    {
        "name": "三叉戟阵型战术2 (Trips Formation Play 2)",
        "desc": "三人紧密排列在右侧，C开球后保护口袋并观察防守分配，QB五步后撤等待路线展开，最外侧WR跑深远Fly路线拉走角卫纵深，第二WR跑Corner路线占据中层边线，内侧槽位跑5码Out路线占据短边线，左侧单独WR在防守将全部注意力放在右侧三叉戟时悄然跑Post路线切入中央深处。防守在强侧因拥挤而导致多人互相阻挡失去对位，弱侧安全卫孤立面对有准备的外接手。\n(Three receivers tightly aligned on the right. C blocks to protect the pocket and reads the defensive distribution. QB takes a 5-step drop and lets routes develop. The outermost WR runs a deep Fly to pull the corner deep. The second WR runs a Corner to occupy the intermediate boundary. The inside slot runs a 5-yard Out to claim the short boundary. The lone left WR, while all defensive attention is on the Trips side, quietly runs a Post deep into the middle. The defense gets congested and loses individual matchups on the strong side. The weak-side safety is left isolated against a prepared receiver.)",
        "标签": ["拥挤失位", "反侧单防弱(Poor Weak Side Coverage)"]
    },
    {
        "name": "三叉戟层叠阵型2 (Trips Stack Play 2)",
        "desc": "三名右侧接球手以前后层叠方式紧密站位而非平行排列，C开球后向后保护口袋，QB三步后撤观察防守者被层叠迷惑后的反应，层叠的三人在开球瞬间几乎同时释放但分别跑向不同方向——最前者跑Fly直冲纵深，第二人跑Corner走边线中层，第三人跑In切入中央，由于开球前的视线遮蔽防守者无法预判谁跑什么路线，区域交接因混乱而完全延误。\n(Three right-side receivers align in a stacked (front-to-back) formation rather than parallel. C blocks backward to protect the pocket. QB takes a 3-step drop and reads the defense's confused reaction to the stack. The three stacked receivers release almost simultaneously but run different directions—the front one runs a Fly straight deep, the second runs a Corner to the intermediate boundary, the third runs an In into the middle. Because the stack hides the receivers pre-snap, defenders cannot predict who will run which route. Zone handoffs are chaotic and completely delayed.)",
        "标签": ["视线遮挡", "交接延误(Poor Stack Coverage)"]
    },
    {
        "name": "三叉戟阵型战术3 (Trips Play 3)",
        "desc": "三人紧密排列在右侧，C开球后推挡保护并注意延迟释放，QB五步后撤用眼神瞄向短距离路线吸引防守前压，前两名接球手跑Hitch和Out短路线故意将防守者吸引向启球线方向，当防守者因拥堵而向前靠拢时，隐藏在层叠后方的第三条路线球员全速冲刺Fly过顶，防守因拥堵出现换人错误且完全忽略了被遮挡的深远威胁。\n(Three receivers tightly aligned on the right. C blocks to protect and watches for delayed release. QB takes a 5-step drop and uses his eyes to look toward the short routes, baiting the defense to step forward. The first two receivers run Hitch and Out short routes, deliberately pulling defenders toward the line of scrimmage. When defenders crowd forward, the third receiver hidden behind the stack sprints on a Fly over the top. The defense, congested, makes assignment-switching errors and completely ignores the obscured deep threat.)",
        "标签": ["过顶忽略", "区域换人错(Poor Deep Coverage and Zone Switching)"]
    },
    {
        "name": "双子阵型战术2 (Twins Formation Play 2)",
        "desc": "左侧并列两名接球手，右侧两名接球手，C开球后保护口袋并注意两侧压力，QB五步后撤阅读防守深度分布，左侧外接跑Fly垂直冲深逼迫安全卫后撤保护身后，内侧槽位同时跑Out路线切向左侧边线短区的空位，右侧WR跑Post路线将安全卫牵制在中路深处使其无法外扩协防，右侧槽位跑Corner路线占据右侧边线纵深，防守因过分忌惮深远路线而整体后撤导致浅区坪区完全交出。\n(Twins formation: two receivers on the left, two on the right. C blocks to protect the pocket and watches both edges. QB takes a 5-step drop and reads the depth of the defense. Left outside WR runs a Fly vertically, forcing the safety to retreat and protect deep. The inside slot simultaneously runs an Out to the left flat. Right WR runs a Post to hold the safety deep in the middle so he can't help outside. Right slot runs a Corner to claim the right boundary deep. The defense, overly afraid of deep routes, retreats as a unit and completely surrenders the shallow flats.)",
        "标签": ["过度后退", "坪区真空(Poor Flat Coverage)"]
    },
    {
        "name": "双子阵型战术3 (Twins Formation Play 3)",
        "desc": "左右各列双接球手，C开球后居中保护，QB七步深撤等待复杂路线组合完全展开，左侧WR跑Post-Corner双变向路线上演假内切转底角的把戏，右侧WR跑Corner-Post双变向先外后内，左侧槽位跑Dig切入中央深处，右侧槽位跑Comeback长回退路线在边线埋伏，四个人的路线完全独立而又同时攻击防线的不同层级和角度，防守者个人脑力和沟通无法同时处理如此复杂的威胁必然顾此失彼。\n(Twins on each side: two receivers left, two right. C blocks in the middle. QB takes a 7-step deep drop and waits for the complex route combinations to fully develop. Left WR runs a Post-Corner double move—faking inside then breaking to the corner. Right WR runs a Corner-Post double move—first outside then back inside. Left slot runs a Dig deep into the middle. Right slot runs a Comeback route lurking on the boundary. All four routes are independent yet simultaneously attack different levels and angles of the defense. The defender's individual brainpower and communication cannot process this many threats at once, inevitably losing track of someone.)",
        "标签": ["复杂路线脑力弱", "顾此失彼(Poor Route Combinations and Coverage)"]
    },
    {
        "name": "双子层叠阵型 (Twins Stack Play)",
        "desc": "左侧两名接球手采用前后层叠站位而非平行站位，C开球后保护口袋并延迟释放到右侧坪区，QB三步后撤观察防守对层叠的反应，层叠的双子在开球后分别向内侧和外侧纵深快速散开，由于层叠的初始站位使防守者对两人的出发方向和距离判断失误，在散开的第一步防守者就失去了贴防位置，防守对散开瞬间的判断根本来不及反应。\n(Two receivers on the left align in a stacked front-to-back formation rather than parallel. C blocks to protect the pocket and releases late to the right flat. QB takes a 3-step drop and reads the defense's reaction to the stack. After the snap, the stacked twins quickly scatter—one inside, one outside deep. Because the stack's starting alignment tricks defenders on release direction and distance, defenders lose tight coverage on the very first step. The defense can't react in time to the scatter moment.)",
        "标签": ["初始散开判断差", "贴防丢失(Poor Tight Coverage)"]
    },
    {
        "name": "双子层叠阵型2 (Twins Stack Play 2)",
        "desc": "左侧双子层叠站位，C开球后向前推挡后释放走斜插路线到中央，QB两步后撤快速出球利用防守尚未建立对位的时间差，层叠两接球手在开球瞬间做内外夹角跑动——一人向外切平路一人向内切斜插，两人的路线在3码处交叉通过，面对区域防守利用快发抢先手在防线未稳时出球，面对人盯人则利用相互挡住交叉的防守者制造拉扯空间，无论何种防守体系应变都过于僵硬难以立即调整。\n(Left side twins stacked. C blocks forward then releases on a Slant into the middle. QB takes a 2-step drop and gets the ball out quickly, exploiting the defense before matchups are set. At the snap, the stacked twins run an inside-outside angle combo—one cuts outside on a flat, the other cuts inside on a Slant. Their routes cross at 3 yards. Against zone, the quick release catches the defense before the coverage is settled. Against man, the crossing routes create a rub that picks defenders. Either defensive system is too rigid to adjust immediately.)",
        "标签": ["应变僵硬", "补位失灵(Poor Help Coverage)"]
    },
    {
        "name": "集结阵型战术1 (Bunch Play 1)",
        "desc": "三名接球手在启球线一侧紧密集结形成拥挤的一堆，C开球后推挡后释放向另一侧短区，QB三步后撤观察防守者被集结混乱后的对位分配，集结的三人开球后同时启动——中锋位负责推挡后走Corner撕开后退，前锋位向弱侧释放，外侧外接手走Fly垂直纵深清空后方，人盯人防守在紧密集结的发球瞬间根本无法迅速辨识并跟住自己的对位人导致被集体淹没。\n(Three receivers form a tight bunch on one side of the line of scrimmage. C blocks then releases toward the other side short area. QB takes a 3-step drop and reads the defense's matchup confusion after the bunch. The three bunched receivers launch simultaneously—the middle runs a Corner to tear back deep, the front releases to the weak side, the outside runs a Fly vertically deep to clear the back. Man coverage, at the snap from a tight bunch, simply cannot quickly identify and track individual assignments and gets collectively overwhelmed.)",
        "标签": ["盯人淹没", "错位跟丢(Poor Man Coverage)"]
    },
    {
        "name": "集结阵型战术2 (Bunch Play 2)",
        "desc": "三人紧密集结在右侧，C开球后保护口袋并注意突击者，QB两步快速后撤将球传向浅区，集结中的外接两人同时跑Corner路线从密集人群中冲出直插边线纵深中深区域，迫使整条防守线集体后退保护深区，此时RB从集结后方悄然释放到右侧空旷的坪区接快速短传，防守被深路线整齐地后退保护但因后退过度导致浅区彻底成为覆盖真空。\n(Three receivers tightly bunched on the right. C blocks the pocket and watches for blitzers. QB takes a quick 2-step drop and throws to the shallow area. Two of the bunched receivers simultaneously run Corner routes, bursting out of the tight group and attacking the boundary intermediate-deep area. This forces the entire defensive line to retreat and protect deep. Meanwhile, RB quietly releases from behind the bunch to the wide-open right flat for a quick short pass. The defense, retreating in unison to protect deep, over-commits and leaves the shallow area a complete coverage vacuum.)",
        "标签": ["浅区真空", "后退过深(Poor Shallow Coverage)"]
    },
    {
        "name": "集结阵型战术3 (Bunch Play 3)",
        "desc": "三人紧密集结在右侧，C开球后立即向左侧短区释放不给防守反应时间，QB两步后撤快速出球，集结中的近端球员沿启球线快速横向跑动向弱侧跑Slant，利用右侧两名外接跑Corner和Post深路线将防守主力全部拖在右侧深区和中路，防守将绝大部分注意力和人员集中在球侧的堆挤区导致完全忽略了弱侧的近端横穿路线，C在端区附近接球时面前空旷无人。\n(Three receivers tightly bunched on the right. C immediately releases to the left short area after the snap, giving the defense no time to react. QB takes a 2-step drop and throws quickly. The near-side player in the bunch runs a fast horizontal route along the line of scrimmage toward the weak side on a Slant. The two outside receivers on the right run Corner and Post deep routes, dragging all defensive attention to the right deep and middle areas. The defense focuses almost all attention and personnel on the bunched side, completely ignoring the weak-side crosser. C catches the ball near the end zone with open field ahead.)",
        "标签": ["弱侧盲区", "中卫漏防(Poor Middle Coverage)"]
    },
    {
        "name": "I字阵型战术1 (I Formation Play 1)",
        "desc": "经典I字阵型，C开球后向前推挡观察线卫动向后释放到右侧短区，QB五步后撤后面临多重选择阅读防守弱点，后置RB先做阻挡假动作然后走Flat路线向右坪区释放作为最短选项，前置左侧外接跑Post路线切入中央深处攻击安全卫，右侧外接跑Corner路线攻击边线纵深，Slot跑Hitch在8码处回身提供中距离，防守面对如此多的接球点无法在瞬时正确判断进攻重点导致阅读犹豫慢半拍。\n(Classic I-formation. C blocks forward, reads the linebacker movement, then releases to the right short area. QB takes a 5-step drop and faces multiple options, reading the defensive weakness. The deep RB first fakes a block, then releases on a Flat route to the right flat as the shortest option. The front left outside WR runs a Post deep into the middle to attack the safety. Right outside WR runs a Corner to attack the boundary deep. Slot runs a Hitch, turning back at 8 yards to provide an intermediate option. The defense, facing so many receiving threats, cannot instantly diagnose the offensive priority and hesitates in its read.)",
        "标签": ["阅读犹豫", "多层选择(Poor Defensive Reads and Multiple Threats)"]
    },
    {
        "name": "I字阵型战术3 (I Formation Play 3)",
        "desc": "I字阵型，C开球后全力保护为深远路线争取时间，QB七步深撤等待所有路线深入防线，左侧WR跑Fly路线全力冲刺40码以上将安全卫彻底钉死在纵深，右侧WR跑Post路线从外侧向中央深处切入，槽位Slot跑Post路线从另一侧向中央汇合形成双柱态势，RB从I字后场走Wheel路线沿边线冲刷纵深，防守的落位尚未完全稳固就被多条纵深路线同时冲击各层保护来不及建立就被打穿。\n(I-formation. C gives full protection to buy time for deep routes. QB takes a 7-step deep drop and waits for all routes to penetrate the defense. Left WR runs a Fly at full speed, sprinting 40+ yards to completely nail the safety deep. Right WR runs a Post from the outside into the deep middle. Slot runs a Post from the other side toward the middle, creating a dual-post formation. RB from the I-backfield runs a Wheel route along the sideline deep. The defense, before even getting fully set, is hit by multiple deep routes simultaneously—every layer of protection is pierced before it can be established.)",
        "标签": ["快节奏冲击", "落位不稳(Poor Defensive Setup)"]
    },
    {
        "name": "双后场阵型战术2 (Double Back Play 2)",
        "desc": "双后场阵型（两名跑卫站后排），C开球后推挡一步后立即释放到左侧浅区，QB五步后撤同时拥有五个接球选项，左侧WR跑Fly路线直冲纵深将整条左侧防线钉在后场，右侧WR跑Post路线切入中央深区牵制安全卫，槽位跑Corner路线攻击右侧边线纵深，双后场之一的RB1走Flat到右侧坪区做短传选项，RB2走浅横穿从左侧短区横穿到右侧，防守因体能和轮转速度有限根本无法同时覆盖从深区到浅区的五个接应点。\n(Double-back formation: two running backs in the backfield. C blocks for one count then immediately releases to the left shallow area. QB takes a 5-step drop and has five receiving options. Left WR runs a Fly straight deep, pinning the entire left defense deep. Right WR runs a Post into the middle deep to occupy the safety. Slot runs a Corner to attack the right boundary deep. RB1 of the double backs runs a Flat to the right flat as a short option. RB2 runs a shallow cross from the left short area to the right. The defense, limited in stamina and rotation speed, simply cannot cover five receiving threats from deep to shallow simultaneously.)",
        "标签": ["多点覆盖弱", "体能轮转差(Poor Stamina and Rotation)"]
    },
    {
        "name": "端侧反跑 (End Around)",
        "desc": "C开球后向右推挡迷惑防守以为进攻方向在右侧，QB接球后右手做出向右侧RB交球的完整假动作诱导整条防线向右侧移动，实际上QB将球藏在身后交给从左侧横移过来的外侧WR，WR接球后向已经完全撤空的左侧边线全速冲刺，左侧的攻击侧因防守被假交球吸引而全员偏右，左侧的防守者已全部不在防守位置上。\n(C blocks right after the snap to deceive the defense into thinking the play goes right. QB receives the snap and executes a full play-fake with his right hand toward the RB on the right, baiting the entire defense to flow right. Actually, QB hides the ball behind his back and hands it to the outside WR who has crossed from the left. WR receives the ball and sprints at full speed toward the now completely empty left sideline. The left side, abandoned because the defense was pulled by the play-fake, has no defenders left in position.)",
        "标签": ["追球惯性", "假动作被骗(Poor Fake Play Execution)"]
    },
    {
        "name": "反向交叉跑动 (Crossbuck)",
        "desc": "C开球后居中保护，QB接球后RB从右侧向左跑动做出接球姿态，与此同时槽位Slot从左侧向右侧跑动同样做出接球假象，两人在QB身前相交通过形成视觉混淆，防守被双人交叉的假动作诱骗集体涌向一侧，QB实际将球交给最初向右跑动的Slot让其沿右侧边线反向冲刺，或将球交给RB沿左侧突破，防守全部被假交球引至错误的一侧。\n(C blocks in the middle. After the snap, RB runs from right to left making a receiving gesture. Simultaneously, Slot runs from left to right also faking a receiving motion. The two cross in front of QB, creating visual confusion. The defense is baited by the dual crossing fake and flows en masse to one side. QB actually hands the ball to Slot (who initially ran right) to sprint along the right sideline in the opposite direction, or hands to RB to break along the left. The defense is entirely pulled to the wrong side by the fake handoff.)",
        "标签": ["假交球易骗", "防守过激(Poor Defensive Aggression)"]
    },
    {
        "name": "双重反跑 (Double Reverse)",
        "desc": "C开球后推挡保护并注意防线反应，QB首先将球手递手交给从左向右跑动的RB做第一次反向，RB持球继续向右跑做出要突破的样子吸引防守全线朝右追击，在跑动中RB再次将球手递手交给从右侧绕行回来的Slot做第二次反方向转移，Slot接球后沿空旷的左侧边线冲刺，外围WR在此期间悄然向纵深穿插走Fly路线将仅存的安全卫拖入深区，防守被连续两次假动作完全耗尽反应时间后后场已空无一人的开阔地。\n(C blocks to protect and watches the defense's reaction. QB first hands the ball to RB who runs from left to right for the first reverse. RB carries the ball right, faking a breakaway run, attracting the entire defense to pursue right. While running, RB hands the ball to Slot who has looped back from the right for a second reverse transfer. Slot receives the ball and sprints up the empty left sideline. The outside WR, during this time, quietly releases deep on a Fly route, dragging the only remaining safety deep. The defense, exhausted by two consecutive fakes with no reaction time left, leaves the backfield a wide-open empty field.)",
        "标签": ["连续假动作", "后场真空(Poor Defensive Reaction and Exhaustion)"]
    },
    {
        "name": "假双重反跑 (Fake Double Reverse)",
        "desc": "C开球后保护口袋，QB首先将球交向RB做出第一次反跑的样子，RB向右跑动与从右向左跑动的Slot做手递手假动作，两人在场上完整执行双重反跑的肢体动作，防守因害怕被反跑直接突破而集体提前前压收缩防线准备防跑，此时QB实际并未松开球权而是将球牢牢握在手中，待防守全线压上后迅速传给在混乱中已悄然跑向深远Fly或Corner路线的外侧WR过顶得分。\n(C blocks the pocket. QB first fakes a handoff to RB who appears to take the first reverse. RB runs right and executes a fake handoff with Slot who runs right-to-left. The two perform the complete physical motions of a double reverse. The defense, afraid of being beaten by the reverse run, collectively steps forward and tightens to defend the run. QB, however, never actually released the ball—he holds it firmly. Once the defense fully commits forward, QB quickly throws deep to the outside WR who has quietly run a Fly or Corner route and scores over the top of the compressed defense.)",
        "标签": ["防跑前压", "深远过顶(Poor Deep Coverage)"]
    },
    {
        "name": "假三重反跑 (Fake Triple Reverse)",
        "desc": "C开球后推挡保护，QB接球后场上连续出现三次假交球动作——QB→RB→Slot→左外接WR，每个接球球员都做出完整的接球、跑动、再交球姿势，三人的假动作将防守的注意力一层层地吸引到右侧，防守完全被多重假动作耗尽而且应对反跑的模式单一过度投入，真正的持球者是始终未松手的QB，待防线完全偏向右侧后QB转身将球传给空无一人的左侧边路的第五名球员。\n(C blocks to protect. After QB receives the snap, three consecutive fake handoffs occur on the field—QB→RB→Slot→Left WR. Each receiving player performs the complete catch, run, and re-handoff motion. The three fakes layer by layer pull defensive attention to the right side. The defense is completely exhausted by multiple fakes and over-commits to stopping the reverse pattern. The true ball carrier is QB, who has never released the ball. Once the defense fully leans right, QB turns and throws to the completely unguarded left sideline where the fifth receiver waits.)",
        "标签": ["多重假动作", "反向无防(Poor Offense Against Reverse Patterns)"]
    },
    {
        "name": "单侧列阵战术1 (Single Set Play 1)",
        "desc": "四名接球手全部列阵在球场同一侧，只有一名WR单独站在空旷的反侧，C开球后迅速向空旷的反侧释放，QB两步后撤快速判断防守对单侧重兵的应对，强侧的四名接球手按坪区、中等路线、深区路线三个层次同时展开撕开防线，弱侧仅剩的单独WR趁机跑一条Post路线切入被清空的中路纵深，防守将绝大部分人员集中在列阵侧导致弱侧几乎弃守一旦球瞬间转移至反向就是多打少的局面。\n(Four receivers all line up on the same side of the field, with only one WR isolated on the wide-open opposite side. C quickly releases to the empty opposite side after the snap. QB takes a 2-step drop and quickly reads how the defense handles the overload. The four receivers on the strong side simultaneously expand across three levels—flat, intermediate, deep—tearing the defense apart. The lone WR on the weak side takes the opportunity to run a Post into the emptied middle deep. The defense concentrates almost all personnel on the overloaded side, essentially abandoning the weak side. If the ball is instantly transferred to the opposite side, it becomes an outnumbered situation favoring the offense.)",
        "标签": ["弱侧空虚", "重兵偏侧(Poor Weak Side Coverage)"]
    },
    {
        "name": "单侧列阵战术3 (Single Set Play 3)",
        "desc": "全队集中在一侧列阵后，C开球后保护口袋并延迟向弱侧释放，QB五步后撤让强侧的WR跑一组复杂的深交叉路线——从强侧出发横穿整个后场向弱侧深远区域冲刺，由于防守的协防侧移需要从强侧全速横向跑动到弱侧而其横向移动速度和选位判断都不足以在接球手到达之前完成补位，弱侧最后只剩下一个孤立无助的单防者面对有充足准备的外接手。\n(The entire offense aligns on one side. C blocks the pocket and releases late to the weak side. QB takes a 5-step drop and lets the strong-side WR run a complex deep crossing route—starting from the strong side, crossing the entire backfield, and sprinting toward the weak-side deep area. The defense's help rotation requires sprinting laterally at full speed from the strong side to the weak side. Their lateral speed and positioning judgment are insufficient to complete the coverage before the receiver arrives. The weak side is left with only one isolated defender facing a well-prepared receiver.)",
        "标签": ["横移协防慢", "单防劣势(Poor Lateral Coverage and Man Coverage Disadvantage)"]
    },
    {
        "name": "完全分散进攻 (Spread Offense)",
        "desc": "五人最大宽度分散站位将防守网彻底拉开到全场，C开球后居中保护提供口袋，QB三步后撤快速扫描全场找出防守最薄弱的一对一点名攻击，四个接球手各自跑不同的垂直或角位路线——左侧Fly、槽位Corner、另一槽位Post、右侧Dig，每个人的路线独立攻击一个防守者使其被彻底孤立没有队友可以帮忙协防，防守阵中只要有任何一个个体球员速度或技术存在短板就会被在此战术中被无限放大并精准点名。\n(Five players line up at maximum width, spreading the defense across the entire field. C blocks in the middle to provide a pocket. QB takes a 3-step drop and quickly scans the field to identify the weakest one-on-one matchup, then targets that defender. Four receivers each run different vertical or angle routes—left Fly, slot Corner, other slot Post, right Dig. Each route independently attacks a single defender, isolating him completely with no teammate available to help. If any individual defender on the defense has a speed or technique weakness, this concept will magnify it and precisely target it.)",
        "标签": ["单兵能力弱", "被孤立点名(Poor Individual Coverage and Isolation)"]
    },
    {
        "name": "斜穿-坪区路线组合 (Slant-Flat Route Combo)",
        "desc": "C开球后保护中路并注意线卫突击，QB两步后撤快速阅读浅区防守者的动向，槽位Slot从右侧释放跑一条Slant路线以45度角切入中央短区域吸引同侧线卫的注意迫使他做出选择，RB同时从后场向同一侧的坪区释放横向跑动向边线方向，线卫在盯防Slot斜插和追防RB坪区之间只能选择其一，如果线卫选择追踪斜插则QB将球快速传到坪区让RB接球后面对空旷边线推进。\n(C blocks the middle and watches for linebacker blitz. QB takes a 2-step drop and quickly reads the shallow defender's movement. Slot releases from the right on a Slant route, cutting at a 45-degree angle into the short middle, drawing the attention of the same-side linebacker and forcing him to choose. RB simultaneously releases from the backfield to the same-side flat, running laterally toward the sideline. The linebacker can only choose one—cover the Slot's Slant or chase RB's Flat. If the linebacker chases the Slant, QB quickly passes to the flat for RB to catch and run up an empty sideline.)",
        "标签": ["浅区抉择弱", "顾此失彼(Poor Defensive Reads and Coverage)"]
    },
    {
        "name": "柱路-坪区组合 (Post-Flat Combo)",
        "desc": "C开球后向右推挡建立保护并注意外侧冲击，QB五步后撤观察安全卫的反应，右侧WR加速跑Post路线切向中央深处将安全卫被迫后退到深区进行保护，在安全卫被牵制在深度后RB立即从后场释放到同一侧的坪区跑Flat接短传，安全卫因为过度尽责地退到深区导致原本应协防的短坪区域无人补位，RB接球后面前有巨大的跑动推进空间可直接过半场。\n(C blocks right to establish protection and watches for outside pressure. QB takes a 5-step drop and observes the safety's reaction. Right WR accelerates on a Post route, cutting into the deep middle, forcing the safety to retreat deep to protect. Once the safety is occupied deep, RB immediately releases from the backfield to the same-side flat for a short Flat pass. The safety, being overly responsible and retreating deep, leaves the short flat area—which he should have helped cover—completely unguarded. RB catches the ball with massive open-field running room and can gain yards past midfield.)",
        "标签": ["安全卫后退过深", "坪区漏防(Poor Flat Coverage)"]
    },
    {
        "name": "回身-底角组合 (Hitch-Corner Combo)",
        "desc": "C开球后保护口袋为这样的半场攻击争取时间，QB五步后撤阅读同侧两名防守者的反应，右侧外侧WR跑Hitch路线冲刺8码后急停回身做出要接短传的姿态迫使对位角卫不得不向前上提准备防守回身球，内侧槽位在角卫上提暴露身后空间的同一瞬间跑Corner路线从内侧绕过角卫全速冲向边线底角的纵深方向，角卫在没有高处安全卫协防的情况下对上提防Hitch和后退防Corner只能二选一。\n(C blocks the pocket to buy time for this half-field attack. QB takes a 5-step drop and reads the reaction of the two defenders on the same side. The right outside WR runs a Hitch—sprinting 8 yards, stopping abruptly, and turning back as if to catch a short pass—forcing the corner to step forward to defend the hitch. The inside slot, at the exact moment the corner steps forward and exposes the space behind him, runs a Corner route from inside, bypassing the corner at full speed toward the deep boundary corner. The corner, without high safety help, must choose between stepping up for the Hitch or dropping back for the Corner—he cannot do both.)",
        "标签": ["角卫孤立", "二选一漏洞(Poor Corner Coverage and One-on-One Dilemma)"]
    },
    {
        "name": "高抛-外侧组合 (Fade-Out Combo)",
        "desc": "C开球后全力保护并为深远球提供充裕时间，QB五步后撤将球分配到防守最薄弱的一层，左侧外侧WR直接跑Fade路线冲向边线底角端区高高跃起接高弧传球逼迫对位角卫必须转身全速冲刺跟防，在角卫被拖入深层争顶时槽位突然跑一条Out路线切向边线短区获得完全无人干扰的接球空间，单个防守者无论在速度还是覆盖面积上都无力同时处理这两个垂直层次完全不同的接球威胁。\n(C fully protects and provides ample time for the deep throw. QB takes a 5-step drop and distributes the ball to the defense's weakest layer. Left outside WR runs a Fade directly toward the boundary corner of the end zone, elevating to catch a high-arc pass, forcing the corner to turn and sprint at full speed to defend. While the corner is dragged deep for the jump ball, the slot suddenly runs an Out route toward the boundary short area, getting completely uncontested receiving space. A single defender, regardless of speed or coverage range, cannot simultaneously defend these two threats at completely different vertical levels.)",
        "标签": ["纵向拉伸防弱", "浅区空位(Poor Vertical Stretch and Shallow Vacancies)"]
    },
    {
        "name": "粉碎概念 (Smash Concept)",
        "desc": "C开球后推挡保护，QB五步后撤阅读边角区域的防守结构，同侧外接两人中靠外的WR跑Corner路线全速冲向边线底角纵深处强力争夺边角区域，内侧的槽接WR跑Hitch路线在8码处急停回身提供快速短传选项，防守方的外角卫和内对位者在面对一个深边角加一个短回身的组合时无法形成有效呼应，不论防守如何选择都必然在其中一个点形成一对一进攻方的优势接球。\n(C blocks to protect. QB takes a 5-step drop and reads the defensive structure in the boundary-corner area. Of the two receivers on the same side, the outside WR runs a Corner route at full speed toward the deep boundary corner, aggressively attacking that space. The inside slot runs a Hitch route, stopping at 8 yards and turning back to provide a quick short option. The defense's outside corner and inside defender, when facing the combination of a deep corner route and a short hitch, cannot effectively coordinate. No matter how the defense chooses, one of the two points will inevitably become a favorable one-on-one matchup for the offense.)",
        "标签": ["边角防呼应差", "结构劣势(Poor Boundary Coverage and Structural Disadvantage)"]
    },
    {
        "name": "网格交叉概念 (Mesh Concept)",
        "desc": "C开球后保护中路，QB三步后撤观察浅区交叉的进展，左侧Slot和右侧Slot两人从场地的相对方向同时以中等速度向启球线附近的浅区跑Drag路线，两人的路线在场地中央3-4码处交错通过形成一道流动的网格屏障，左侧WR跑Fly清空左侧纵深，右侧WR跑Corner清空右侧纵深，跑Draw的两人在穿过彼此时利用队友身体作为掩护阻挡追防的盯人防守者，防守者因被挂住碰撞而失位后接球手有充足空间接球转身推进。\n(C blocks the middle. QB takes a 3-step drop and watches the shallow crossing develop. Left Slot and Right Slot, from opposite sides of the field, simultaneously run Drag routes at moderate speed across the shallow area near the line of scrimmage. Their routes cross at 3-4 yards in the middle of the field, forming a moving mesh barrier. Left WR runs a Fly to clear the left deep. Right WR runs a Corner to clear the right deep. The two Drag runners, as they cross, use each other's body as a natural screen to obstruct pursuing man defenders. Defenders get rubbed off and knocked out of position. The receiver has ample space to catch, turn, and run after catch.)",
        "标签": ["盯人掩护挂", "交叉失位(Poor Man Coverage and loose position while crossing)"]
    },
    {
        "name": "四条垂直路线 (Four Verticals)",
        "desc": "C开球后全力保护口袋为所有路线争取深球时间并观察是否有防守者漏进后场，QB七步深撤扫描全场安全卫的移动选择，四个接球手（左右外侧WR加两个槽位Slot）同时全速垂直冲刺各自直线冲向对方最深区域，四个深路线同时冲击迫使防守全线拼命后退保护深区，RB在四人都冲向纵深时悄然从后场释放到中路浅坪区，防守在同一次攻防中仅凭场上人数根本无法安全包夹四条深路线外加守一个浅坪跑卫。\n(C gives full pocket protection to buy time for all routes and watches for any defender leaking into the backfield. QB takes a 7-step deep drop and scans the safety's movement across the field. Four receivers—both outside WRs and both Slots—simultaneously sprint vertically at full speed, each running straight toward the deepest part of the field. Four deep routes hit at once, forcing the entire defense to desperately retreat to protect deep. RB, while all four are going deep, quietly releases from the backfield into the middle shallow flat. The defense, with only the players on the field, simply cannot safely bracket four deep routes AND cover a shallow flat running back on the same play.)",
        "标签": ["纵深兵力不足(Poor Deep Coverage)"]
    },
     {
        "name": "Snag 概念 (Snag Concept)",
        "desc": "C开球后居中保护口袋，QB三步后撤先阅读强侧。强侧最外侧WR跑Corner路线直插边线纵深12码处，吸引角卫和安全卫的注意力制造高位威胁；同侧槽位Slot跑Snag路线，先垂直冲击4码后急停回身以45度斜插向外侧寻找空档；RB从后场直接释放到强侧的坪区路线提供低位快传选项。三条路线形成一个三角形路线组合，迫使浅区防守者在高低位和水平位同时面临三打二的兵力劣势。\n(C protects the pocket after snap. QB takes a 3-step drop and reads the strong side first. The outside WR to the strong side runs a Corner route attacking the sideline at 12 yards to draw corner and safety attention; the Slot receiver on the same side executes a Snag route, driving vertically for 4 yards before stopping and slanting outward at a 45-degree angle to find open space; the RB releases directly into the flat on the strong side as a low, quick outlet. The three routes form a triangle concept, forcing the shallow defender into a high-low bind and a horizontal stretch against a 3-on-2 disadvantage.)",
        "标签": ["区域交接模糊 (Zone handoff confusion); 浅区兵力劣势 (Shallow numerical disadvantage)"]
    },
    {
        "name": "Stick 概念 (Stick Concept)",
        "desc": "C开球后保护口袋并注意突击，QB三步后撤后视线锁定强侧的Stick路线组合。强侧最外侧WR跑垂直Fly路线全速冲击底线迫使角卫转身跟深；同侧槽位Slot跑5码折回身路线急停回身；而RB则在启球线后以Stick路线直冲5码后迅速外摆到外侧坪区。这种高低-外的组合拳，面对区域防守或人盯人都能迫使对手在回身与坪区之间做出艰难选择。\n(C protects the pocket after snap. QB takes a 3-step drop targeting the Stick combination. The outside WR on the strong side runs a vertical Fly to pin the corner deep; the strong-side Slot runs a 5-yard Hitch, stopping and turning back to the QB; the RB releases from behind the line on a Stick route, driving 5 yards then breaking out to the flat. This high-low-out combo forces defenders to commit between the hitch and the flat, regardless of coverage.)",
        "标签": ["浅区抉择弱 (Poor shallow decision); 三点漏一 (Three points, one left open); 阅读犹豫 (Hesitant read)"]
    },
    {
        "name": "Flood 概念/水淹 (Sail Concept)",
        "desc": "C开球后全力向右推挡保护，QB五步后撤并启动假跑动作吸引线卫前压。右侧外侧WR跑垂直冲刺牵制底线防守；槽位Slot在12-14码处以“速度式直角外切”全速跑向边线创造中距离大空档；RB立刻短距离外摆至右侧坪区。瞬间在单侧形成深、中、短三层垂直维度的一波流“水淹”，直接制造三对二的区域过载。\n(C protects the pocket with a strong slide right. QB takes a 5-step drop with a play-action fake. The right-side WR runs a vertical streak to occupy the deep defender; the Slot runs a 12-14 yard 'speed out' to the sideline at full speed; the RB flares into the right flat. In an instant, a flood of receivers overwhelms that side, creating a deep-mid-short layered stretch and a direct 3-on-2 zone overload.)",
        "标签": ["区域衔接差 (Poor zone connectivity); 弱侧补防慢 (Slow weak-side recovery); 窄边防守人数劣势 (Short-side numbers disadvantage)"]
    },
    {
        "name": "Mills 概念 (Mills Concept)",
        "desc": "C开球后严密保护口袋，QB在假跑交球后执行七步深撤。右侧外接手先向内急加速跑10码然后90度角切入场地中央形成Dig路线，吸引全场唯一的安全卫上提封堵；在安全卫移动的瞬间，左侧同方向的槽外接立刻趁着中路真空以弧线高速绕后跑Post路线直接攻击全场最深的防守腹地。\n(C holds the pocket after a hard play-fake. The Outside WR on the strong side runs a Deep Dig route, driving hard 10-12 yards then cutting 90° inside to occupy the single-high safety; the moment the safety steps up, a Slot receiver or opposite-side WR bursts from the backside running a post route over the top, exploiting the vacated middle deep zone.)",
        "标签": ["安全卫外扩 (Safety over-expanded); 中路纵深空 (Open middle deep); 安全卫阅读激进 (Aggressive safety read)"]
    },
    {
        "name": "Scissors 概念 (Scissors Concept)",
        "desc": "C开球后居中保护并观察防守纵深，QB五步后撤。左侧并列站位（Twins），内侧外接跑 Corner 路线直接切向外侧底角，强迫同侧防守角卫迅速向外侧移动；而外侧外接则在防守人向外扩张的瞬间，以一个 Post 路线从外向内切向场地中央。两人路线形成一把张开的“剪刀”，利用防守者对外部底角的防守反应来暴露中路衔接区的巨大漏洞。\n(C protects the center pocket. From a Twins alignment, the inside WR sprints vertically then breaks sharply to the deep corner; the Outside WR, on the release of the corner route, cuts inside on a deep Post. The routes create a 'Scissors' action that forces the cornerback to widen while the safety gets caught between the two deep cuts, opening up the middle seam.)",
        "标签": ["安全卫协防弱 (Weak safety help); 预判被骗 (Susceptible to misdirection)"]
    },
    {
        "name": "Drive 概念 (Drive Concept)",
        "desc": "C开球后保护口袋并提防内侧，QB五步后撤。弱侧外侧大外接全速冲刺 Fly 路线清空后方；近端锋或槽外接在5码内横穿 Drag 路线吸引线卫紧跟；紧接着，位于同侧后方的另一外接手则猛然加速跑一个较深的 Dig 路线（10-15码）直插因横穿路线造成的防守分层瞬间空出的中腹空地。\n(C protects the pocket. The backside WR clears by running a vertical Fly. The nearby Slot or TE runs a shallow Drag route (0-5 yards) to occupy the linebacker’s eyes. The remaining receiver on that side then accelerates into the void behind the drag, running a deeper Dig route (10-15 yards) into the intermediate middle zone.)",
        "标签": ["横移补位慢 (Slow lateral fill); 中场真空 (Vacant midfield area)"]
    },
    {
        "name": "Dragon 概念 (Slant-Flat Combo 加强版)",
        "desc": "C开球后快速推挡并准备释放，QB执行三步快速后撤。左侧WR全力垂直冲刺拉空半场；右侧槽外接执行立刻执行横跨启球线的长距离 Drag 吸引视野；同时右侧RB迅速释放至右外侧坪区。所有接球点全部清洗走防守人后，中锋C从中路悄然释放接球，面前空无一人。\n(C blocks and then releases into the vacated middle. The left WR runs a vertical to clear out the zone; the Slot to the right runs a shallow Drag crossing the field to occupy box defenders; the RB immediately releases to the right flat. As all defenders are dragged away, the Center slips untouched into the wide-open center field for an easy catch.)",
        "标签": ["忽略中锋 (Center ignored as receiver); 中路纵向空 (Open vertical middle lane)"]
    },
    {
        "name": "费城特供 (Philly Special)",
        "desc": "C将球开给QB后立刻假装漏人向右侧阻挡，QB接球后立刻将球向后抛给左侧反向冲刺而来的RB，QB自己则向右侧悄然溜边。RB持球后抬头佯冲一步内线迫使防守者收窄，随即将球横向传给早已埋伏在右侧且无人看管的QB，QB原地接球后直接送出跨越全场的长传达阵。\n(C snaps to the QB and immediately acts as if blocking right. The QB quickly pitches the ball backward to a RB sweeping left, then the QB drifts right along the sideline unnoticed. The RB takes one step upfield to freeze the defense, then throws a lateral back to the wide-open QB who delivers a deep cross-field touchdown pass.)",
        "标签": ["多重假动作 (Breakdown against multiple fakes); 追球惯性 (Ball-watching overcommit)"]
    },
    {
        "name": "特殊选项 (RPO - Run Pass Option)",
        "desc": "C开球后负责推挡左半侧防守截锋，QB和RB在做假交球时密切观察左侧线卫：如果线卫为了防跑而前压封堵内侧缝隙，QB立刻收回球权并越过线卫头顶快速传给左侧外接手的短距离 Slant 路线；如果线卫后退进入防传区域，QB则真实将球交给RB执行冲球推进。\n(C protects the left gap. The QB reads the left Inside Linebacker during the mesh with the RB. If the linebacker steps up for run support, the QB pulls the ball and throws a quick Slant to the left WR. If the linebacker drops back into coverage, the QB leaves the ball with the RB for a quick inside run.)",
        "标签": ["阅读犹豫 (Hesitant read); 防守过激 (Over-aggressive pursuit)"]
    },
    {
        "name": "快速气泡屏风 (Quick Bubble Screen)",
        "desc": "C开球后快速向右移动实施对外侧角卫的阻挡，QB接球后不做调整立刻平传至外侧槽外接，外侧大外接开球后也立即转身向内阻挡安全卫或清场。三人瞬间完成接球、清道、推进，将攻击点设立在场地的绝对边路。\n(C snaps the ball and moves quickly to block the outside corner. The QB immediately throws a horizontal pass to the Slot. The outside WR immediately turns inside to block the advancing safety. This creates a immediate convoy along the sideline to attack the field's edge with speed.)",
        "标签": ["边路纵深空 (Open sideline deep); 边角防呼应差 (Poor sideline coordination)"]
    },
    {
        "name": "短抛屏风 (Tunnel Screen)",
        "desc": "C和RB开球后立刻放弃中路防守人转而在启球线后横向移动组成开路小组；外侧大外接则先向前佯装冲刺两步后，迅速回身“钻进”开路小组组成的移动城墙后面接QB的平传球。其他接球手全部垂直冲深清空后方，为屏风接球手创造广阔的持球推进路线。\n(The offensive line lets the rushers through, then the C and RB slide immediately to the sideline to form a moving wall. The Slot receiver fakes a vertical release for two steps then 'tunnels' back inside towards the QB’s throw. The outside receivers run deep clears, opening a massive rushing lane for the screen receiver behind his blockers.)",
        "标签": ["防守前压 (Heavy Blitz / Overcommit); 浅区跑动空间 (Shallow running lanes open)"]
    },
    {
        "name": "Dagger 概念 (Dagger Concept)",
        "desc": "C开球后滞留并加强口袋深度，QB在假动作后执行七步深撤。弱侧近端锋或外接手全速启动沿中路的接缝跑 Seam 路线垂直冲击后场，吸引高位安全卫的协防；同侧大外接则全力冲刺到底后在场地中央17-20码深处执行极长的Dig路线横穿全场。利用Seam路线的纵向威胁将安全卫“定住”，专门打击单高卫防阵的横向覆盖死角。\n(C stays in to protect for depth. The backside receiver runs a vertical Seam route to lock the high safety in place; the primary outside WR runs a deep crossing route (Inside Dig, 17-20 yards deep) behind the linebacker level but in front of the stationary safety. This specifically attacks the horizontal weakness of single-high safety defenses.)",
        "标签": ["纵深兵力不足 (Insufficient deep coverage); 中场防跑动能力弱 (Weak middle field run defense)"]
    },
    {
        "name": "Hoss 概念 (Hitch-Seam Combo 加强版)",
        "desc": "C开球后退守中路，QB根据开球前判断选择阅读侧。强侧外侧外接跑垂直 Seam 路线利用速度拉开与边线之间的距离；内侧槽外接果断在8码处折回做回身路线。四分卫首先阅读安全卫的动态：如果安全卫向前补位防止回身，就直接传 Seam 路线；如果安全卫后退保护纵深，则快速传给回身路线获取稳健码数。\n(C stays home for pass protection. The outside WR runs a vertical Seam reading the safety; the inside Slot runs a hard 8-yard Hitch. The QB reads the deep safety: if the safety jumps the hitch, the QB rips the ball to the Seam; if the safety bails deep, the QB checks it down to the hitch immediately.)",
        "标签": ["安全卫协防弱 (Weak safety help); 角卫孤立 (Cornerback isolated)"]
    },
    {
        "name": "Divide 概念 (Divide Concept)",
        "desc": "C开球后居中保护，QB执行三步快速阅读。左侧两个并列站位外接手互相交叉，内侧近端锋跑 Corner 杀向外侧底角，外侧外接跑 Post 切向中路立柱；右侧单站的大外接跑垂直冲刺清空另半侧。核心在于双人路线在二线防守区交叉“分流”，瞬间把高位安全卫钉死在葫芦口无法同时覆盖两边。\n(C protects the middle. From a Twins alignment on the left, the inside receiver runs a Corner towards the pylon while the outside receiver breaks on a Post toward the middle; the right-side receiver clears with a Fly. The two routes 'divide' the deep coverage, creating a millisecond of indecision for the safety and cornerback, leaving one receiver wide open.)",
        "标签": ["区域换人错 (Zone exchange errors); 纵深区域沟通失误 (Deep zone communication failure)"]
    },
    {
        "name": "Slot Fade 特殊 (66 Concept)",
        "desc": "C开球后向右推挡保护口袋右侧，QB将球高吊抛出。右侧大外接全力冲刺跑 Post 路线吸引角卫向中路内收移动；就在角卫转身向内跟防的瞬间，内部槽外接以最快速度从槽位冲出并侧身沿边线跑 Fade 路线，接QB的高弧线吊球攻击边线与角卫无法转身覆盖的盲区。\n(C slide protects to the right. The outside WR runs a hard inside Post to occupy the cornerback; the Slot receiver immediately bursts to the outside running a Fade down the numbers. With the corner turned inward, the QB drops a high-arching ball into the sideline void before the safety can rotate over.)",
        "标签": ["争顶劣势 (Poor 50/50 ball ability); 角卫转身不便 (Cornerback poor turn ability)"]
    },
    {
        "name": "Yankee 概念 (Yankee Concept)",
        "desc": "C开球后执行极度逼真的假跑开路动作，全体接球手先假装阻挡，诱使线卫和全体防守前压；待防守全线收缩至启球线附近预备防跑时，左侧大外接突然从内线绕出跑 Post 路线攻击后场，右侧速度极快的槽外接则在深远后方跑 Dig 路线横穿半场。利用极致的假跑虚晃创造出深远单挑的安全卫噩梦。\n(The entire offense sells a hard run fake with the C firing out to block. While the defense bites up to stop the run, the left WR takes an inside release on a deep Post and the right Slot runs a deep crossing route over the flat-footed safeties. This is a devastating play-action shot designed to punish aggressive run defense.)",
        "标签": ["防跑前压 (Run defense creep); 假动作判断失误 (Fooled by play action)"]
    },
    {
        "name": "Smash-Whip 变种 (Smash-Whip Variant)",
        "desc": "C开球后推挡保护，QB五步后撤阅读边角区域。外侧大外接执行10码的 Corner 路线冲击底角；槽外接没有跑常规的快速回身，而是执行“Whip”路线：先假装向内侧斜插，当防守者重心向内移动试图切断回身球时，突然甩向边线。利用鞭打效应制造瞬间脱离。\n(The Outside WR attacks the deep corner pylon to widen the defense. The Slot receiver does not sit in a soft spot; instead he runs a Whip route: hard fake inside as if to sit, then whips back outside towards the flat. This whipping action creates instant separation from the defender expecting a hitch.)",
        "标签": ["连续变向弱 (Weak consecutive cuts); 惯性冻结 (Momentum freeze)"]
    },
    {
        "name": "Y-Juke 概念 (Hoss Y-Juke)",
        "desc": "C开球后强力保护内侧；两个外侧大外接分别从两侧全速跑垂直 Seam 路线将线卫和“安全卫”死钉在中场；中路的灵活接球手（Y）开球后跑 Juke 路线：先向内侧横向晃动牵制，随后立即向外侧平移寻找中路的天然草坪空地进行接球。这种支开锋线防守人的技巧，专门攻击 Cover 2 中间深洞。\n(The outside WRs run vertical seams to clear out the middle. The designated 'Y' receiver runs a Juke route: an initial shake inside to freeze the middle linebacker, then a sudden lateral break outside to find 'green grass' in the middle. A targeted attack on the deep middle void of Cover 2/Tampa 2.)",
        "标签": ["安全卫后退过深 (Safety dropping too deep); 球场中央区域空洞 (Vacant middle of the field)"]
    }
    

]


# ==================== 构建索引 ====================
tactics_index = [{"name": t["name"], "tags": t["标签"]} for t in tactics_full]
index_text = ""
for i, t in enumerate(tactics_index, 1):
    index_text += f"{i}. {t['name']} [{', '.join(t['tags'])}]\n"

all_tags = list(set(tag for t in tactics_full for tag in t["标签"]))
all_tags_string = "，".join(all_tags)


def get_full_desc(names):
    result = ""
    for name in names:
        for t in tactics_full:
            if t["name"] == name:
                result += f"\n【{t['name']}】\n{t['desc']}\n标签: {', '.join(t['标签'])}\n"
                break
    return result
# ==================== 构建索引 ====================
# 使用 .get() 方法安全获取标签，如果没有则使用空列表
tactics_index = []
for t in tactics_full:
    # 获取标签，兼容可能的字段名
    tags = t.get("标签", t.get("tags", t.get("Tag", [])))
    # 如果tags是字符串，转换为列表
    if isinstance(tags, str):
        tags = [tags]
    tactics_index.append({"name": t["name"], "tags": tags})

index_text = ""
for i, t in enumerate(tactics_index, 1):
    if t["tags"]:  # 只有当有标签时才显示
        index_text += f"{i}. {t['name']} [{', '.join(t['tags'])}]\n"
    else:
        index_text += f"{i}. {t['name']} [无标签]\n"

# 收集所有标签（跳过空的和字符串类型的）
all_tags = set()
for t in tactics_full:
    tags = t.get("标签", t.get("tags", t.get("Tag", [])))
    if isinstance(tags, list):
        all_tags.update(tags)
    elif isinstance(tags, str):
        all_tags.add(tags)
all_tags_string = "，".join(sorted(all_tags))

# ==================== 语言选择 ====================
st.sidebar.header("🌐 Language / 语言")
language = st.sidebar.radio("选择输出语言 / Select output language:", ["中文", "English"], horizontal=True)

if language == "English":
    L = {
        "lang_instr": "Please respond in English.",
        "best": "🏆 Best Tactic:",
        "reason": "📝 Why this tactic:",
        "exec": "⚡ Key execution points:",
        "expect": "📊 Expected result:",
        "backup": "🔄 Backup tactic:",
        "switch": "🔀 When to switch:",
        "weak_found": "🎯 AI identified weaknesses:",
        "weak_none": "ℹ️ Could not extract clear weakness tags, matching based on overall description.",
        "cand_found": "✅ Phase 1 done, {} candidates from 54 tactics:",
        "spinner1": "🔍 Phase 1/2: Analyzing your description and extracting key weaknesses...",
        "spinner2": "🎯 Phase 2/2: Selecting the best tactic from candidates...",
        "done": "✅ Tactical analysis complete!",
        "button": "Analyze & Recommend Tactics",
        "warn": "Please describe the game situation first.",
        "header": "📋 Game Situation",
        "ph": "e.g.: Their DBs are slow, safety plays too deep. We're down 3 with 2 min left. Need quick yards...",
        "pref": "Preference:",
        "pref_opts": ["Balance mode", "Safe (highly short passes safe but might not be effective)", "Aggressive (normally deep strikes，risky!!!)"],
        "error1": "No candidates found. Please describe the situation in more detail.",
        "error2": "Phase 1 failed:",
        "error3": "Phase 2 failed:",
    }
else:
    L = {
        "lang_instr": "请用中文回答。",
        "best": "🏆 最佳战术：",
        "reason": "📝 推荐理由：",
        "exec": "⚡ 执行要点：",
        "expect": "📊 预估效果：",
        "backup": "🔄 备选战术：",
        "switch": "🔀 切换时机：",
        "weak_found": "🎯 AI 识别到的弱点：",
        "weak_none": "ℹ️ AI 未能提取到明确的弱点标签，将根据整体描述进行匹配。",
        "cand_found": "✅ 初筛完成，从54条中选出 {} 条候选：",
        "spinner1": "🔍 阶段1/2：AI 正在理解你的描述，并提取关键弱点...",
        "spinner2": "🎯 阶段2/2：正在从候选中精选最佳战术...",
        "done": "✅ 战术分析完成！",
        "button": "分析比赛并推荐战术",
        "warn": "请先输入比赛情况描述。",
        "header": "📋 比赛情况描述",
        "ph": "例如：对方防守球员速度偏慢，安全卫站位太深，我们落后3分，还剩2分钟，需要快速推进...",
        "pref": "偏好：",
        "pref_opts": ["平衡模式", "优先安全战术（高成功率，短传为主）", "优先激进战术（深远打击，风险高！！！）"],
        "error1": "初筛未返回结果，请尝试更详细地描述比赛情况。",
        "error2": "初筛失败:",
        "error3": "精选阶段失败:",
    }

# ==================== 用户输入 ====================
st.sidebar.header(L["header"])
st.sidebar.markdown("---")
if language == "English":
    st.sidebar.caption(f"📊 Queries this session: {st.session_state.query_count}")
else:
    st.sidebar.caption(f"📊 本次会话查询次数：{st.session_state.query_count}")

free_text = st.sidebar.text_area(L["header"], placeholder=L["ph"], height=200)

need_quick = st.sidebar.radio(L["pref"], L["pref_opts"])

# ==================== 标题 ====================
st.title("🏈 腰旗战术官" if language == "中文" else "🏈 FLAG TACTICS MANAGER")
st.markdown(
    f"输入比赛信息,我们将帮你自动筛选最佳方案。"
    if language == "中文"
    else f"Describe the game situation. We'll analyze and recommend the best tactics combinations for you."
)
# ==================== 🎨 UI: 关于本项目 ====================
with st.expander("📌 About" if language == "English" else "📌 关于本项目", expanded=False):
    if language == "English":
        st.markdown("""
        ### 🏈 FLAG TACTICS MANAGER
        
        This tool combines:
        - **50+ curated flag football tactics** with bilingual descriptions
        - **AI-powered weakness detection** from your description of the game
        - **Two-stage tactical matching** for precise recommendations
        - **Interactive route library** with 25 core routes
        - **Built with:** Python · Streamlit · OpenAI API
        
        *Created by a highschool flag football lover who is willing to interpret this sports to the world.*
        """)
    else:
        st.markdown("""
        ### 🏈 腰旗橄榄球战术官
        
        本工具融合了：
        - **50+ 条精心整理的腰旗战术**，含中英双语详解
        - **AI 弱点识别**，从你的比赛描述中提取防守漏洞
        - **两阶段战术匹配**，确保推荐精准度
        - **交互式路线大全**，涵盖 25 条核心路线
        - **技术栈：** Python · Streamlit · OpenAI API
        
        *由热爱腰旗橄榄球的高中生开发。*
        """)
        # ==================== 🎨 UI: 路线大全（卡片按钮式UI）====================
# 25条路线数据（中英文名称 + 详细描述）
route_reference = [
    {
        "en": "Fly",
        "zh": "飞驰路线",
        "desc_zh": "全速垂直冲刺，无任何变向，直接攻击纵深。",
        "desc_en": "Full-speed vertical sprint with no cuts, directly attacks the deep area.",
        "category": "垂直路线"
    },
    {
        "en": "Hitch",
        "zh": "回身路线",
        "desc_zh": "冲刺约5-7码后急停，转身回跑2-3码面向四分卫。",
        "desc_en": "Sprint 5-7 yards, stop abruptly, turn back 2-3 yards to face the QB.",
        "category": "短距离路线"
    },
    {
        "en": "Slant",
        "zh": "斜插路线",
        "desc_zh": "向前2-3码后，以45°角快速斜插进入中路。",
        "desc_en": "After 2-3 yards, cut at a 45° angle inside to the middle.",
        "category": "内切路线"
    },
    {
        "en": "Out",
        "zh": "外侧直角路线",
        "desc_zh": "直线跑5-7码后，以90°直角切向外侧边线。",
        "desc_en": "Run straight 5-7 yards, then break at a 90° angle toward the sideline.",
        "category": "外切路线"
    },
    {
        "en": "In",
        "zh": "内侧直角路线",
        "desc_zh": "直线跑5-7码后，以90°直角切向内侧中央。",
        "desc_en": "Run straight 5-7 yards, then break at a 90° angle toward the middle.",
        "category": "内切路线"
    },
    {
        "en": "Post",
        "zh": "柱状路线",
        "desc_zh": "加速7-10码后45°内切，直指球门立柱方向。",
        "desc_en": "Accelerate 7-10 yards, then cut inside at 45° toward the goalpost.",
        "category": "深远路线"
    },
    {
        "en": "Corner",
        "zh": "底角路线",
        "desc_zh": "冲刺约7-10码后45°外切，攻击端区底角。",
        "desc_en": "Sprint 7-10 yards, then break outside at 45° toward the end‑zone corner.",
        "category": "深远路线"
    },
    {
        "en": "Post-Corner",
        "zh": "柱角假动作",
        "desc_zh": "先做Post内切假动作，二次变向切向外侧底角。",
        "desc_en": "Fake a Post inside, then double‑move to the outside corner.",
        "category": "双变向路线"
    },
    {
        "en": "Corner-Post",
        "zh": "角柱假动作",
        "desc_zh": "先做Corner外切假动作，再快速切回内侧中央。",
        "desc_en": "Fake a Corner outside, then quickly cut back inside to the middle.",
        "category": "双变向路线"
    },
    {
        "en": "Stop and Go",
        "zh": "急停再启动",
        "desc_zh": "冲刺约7码急停，片刻后再次全速冲刺深区。",
        "desc_en": "Sprint about 7 yards, stop, then immediately accelerate deep again.",
        "category": "变速路线"
    },
    {
        "en": "Chair",
        "zh": "座椅路线",
        "desc_zh": "向前4码→横向平移到边线→沿边线垂直冲刺。",
        "desc_en": "Run 4 yards forward, slide laterally to the sideline, then sprint vertically.",
        "category": "组合路线"
    },
    {
        "en": "Option",
        "zh": "选项路线",
        "desc_zh": "根据防守者站位：防内则外切，防外则内切。",
        "desc_en": "Read the defender: break outside if he protects inside, or inside if he protects outside.",
        "category": "阅读路线"
    },
    {
        "en": "Curl",
        "zh": "卷曲路线",
        "desc_zh": "跑动10码后划小弧回身接球，常见于边线。",
        "desc_en": "Run 10 yards, then loop back in a small arc toward the sideline to catch.",
        "category": "回身路线"
    },
    {
        "en": "Comeback",
        "zh": "回退长路线",
        "desc_zh": "深冲12-15码后圆弧折返，向启球线回退。",
        "desc_en": "Sprint 12-15 yards deep, then curl back toward the line of scrimmage.",
        "category": "深远路线"
    },
    {
        "en": "Whip",
        "zh": "鞭打路线",
        "desc_zh": "先假装斜插内侧，再快速甩向外侧平路线。",
        "desc_en": "Fake a slant inside, then quickly whip to the outside flat route.",
        "category": "变向路线"
    },
    {
        "en": "Dig",
        "zh": "深凿路线",
        "desc_zh": "垂直冲10-12码，以近90°角猛切中路。",
        "desc_en": "Sprint 10-12 yards vertically, then drive inside at a near 90° angle.",
        "category": "中距离路线"
    },
    {
        "en": "Fade",
        "zh": "高弧深远路线",
        "desc_zh": "冲向边线底角，接高弧度传球，利用身体优势。",
        "desc_en": "Run to the boundary corner, catch a high‑arc pass using body positioning.",
        "category": "端区路线"
    },
    {
        "en": "Flat",
        "zh": "坪区路线",
        "desc_zh": "横向或斜向跑向启球线附近的边路浅区。",
        "desc_en": "Release laterally to the flat area near the line of scrimmage.",
        "category": "短距离路线"
    },
    {
        "en": "Wheel",
        "zh": "车轮路线",
        "desc_zh": "先横向移动至边路浅区，再突然垂直冲刺。",
        "desc_en": "Start by moving laterally to the flat, then suddenly turn upfield vertically.",
        "category": "跑卫路线"
    },
    {
        "en": "Drag",
        "zh": "拖拽横穿路线",
        "desc_zh": "低速横穿全场，利用队友掩护寻找空位。",
        "desc_en": "Run a shallow cross at moderate speed, using teammates as traffic to get open.",
        "category": "横穿路线"
    },
    {
        "en": "Snag",
        "zh": "斯纳格路线",
        "desc_zh": "垂直冲击4码急停，45°斜插向外侧找空档。",
        "desc_en": "Drive 4 yards vertical, stop, then cut at 45° to the outside to find space.",
        "category": "短距离路线"
    },
    {
        "en": "Stick",
        "zh": "棍棒路线",
        "desc_zh": "垂直推进5码后迅速外摆到外侧坪区。",
        "desc_en": "Push 5 yards vertically, then quickly swing to the outside flat.",
        "category": "短距离路线"
    },
    {
        "en": "Juke",
        "zh": "晃动路线",
        "desc_zh": "先向内侧晃动牵制防守，再向外侧平移接球。",
        "desc_en": "Shake inside to freeze the defender, then slide outside to receive.",
        "category": "晃动路线"
    },
    {
        "en": "Seam",
        "zh": "接缝路线",
        "desc_zh": "垂直冲刺，沿着号码与哈希线之间的接缝区域。",
        "desc_en": "Sprint vertically, staying in the seam between the numbers and the hash marks.",
        "category": "垂直路线"
    },
    {
        "en": "Speed Out",
        "zh": "速度外切",
        "desc_zh": "全速跑12-14码后，以直角高速切向边线。",
        "desc_en": "Run full speed 12-14 yards, then break sharply to the sideline at a right angle.",
        "category": "外切路线"
    }
]

# 根据语言设置文本
if language == "English":
    route_lib_title = "📖 Route Library"
    route_lib_help = "Click any route button to view detailed description"
    category_names = {
        "垂直路线": "Vertical Routes",
        "短距离路线": "Short Routes",
        "内切路线": "Inside Routes",
        "外切路线": "Outside Routes",
        "深远路线": "Deep Routes",
        "双变向路线": "Double Move Routes",
        "变速路线": "Speed Change Routes",
        "组合路线": "Combo Routes",
        "阅读路线": "Option Routes",
        "回身路线": "Comeback Routes",
        "变向路线": "Cut Routes",
        "中距离路线": "Intermediate Routes",
        "端区路线": "End Zone Routes",
        "跑卫路线": "RB Routes",
        "横穿路线": "Crossing Routes",
        "晃动路线": "Juke Routes"
    }
else:
    route_lib_title = "📖 路线大全"
    route_lib_help = "点击任意路线按钮查看详细说明"
    category_names = {
        "垂直路线": "垂直路线",
        "短距离路线": "短距离路线",
        "内切路线": "内切路线",
        "外切路线": "外切路线",
        "深远路线": "深远路线",
        "双变向路线": "双变向路线",
        "变速路线": "变速路线",
        "组合路线": "组合路线",
        "阅读路线": "阅读路线",
        "回身路线": "回身路线",
        "变向路线": "变向路线",
        "中距离路线": "中距离路线",
        "端区路线": "端区路线",
        "跑卫路线": "跑卫路线",
        "横穿路线": "横穿路线",
        "晃动路线": "晃动路线"
    }

# 使用 expander 包裹整个路线大全模块
with st.expander(route_lib_title, expanded=False):
    st.caption(route_lib_help)
    
    # 添加分类筛选器
    categories = list(set([r["category"] for r in route_reference]))
    categories.sort()
    
    # 创建分类选择器
    selected_category = st.selectbox(
        "🏷️ Filter by category" if language == "English" else "🏷️ 按分类筛选",
        ["All"] + [category_names.get(c, c) for c in categories] if language == "English" else ["全部"] + [category_names.get(c, c) for c in categories],
        key="category_filter"
    )
    
    if selected_category == "All" or selected_category == "全部":
        filtered_routes = route_reference
    else:
        # 反向映射找到原始分类名
        for cn, display_name in category_names.items():
            if display_name == selected_category:
                filtered_routes = [r for r in route_reference if r["category"] == cn]
                break
    
    st.markdown("---")
    
    # 使用网格布局显示按钮（每行4个）
    cols_per_row = 4
    for i in range(0, len(filtered_routes), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(filtered_routes):
                route = filtered_routes[idx]
                
                with cols[j]:
                    # 卡片样式（保持原有的视觉效果）
                    if language == "English":
                        card_title = f"**🏈 {route['en']}**"
                        card_subtitle = f"*{route['zh']}*"
                    else:
                        card_title = f"**🏈 {route['zh']}**"
                        card_subtitle = f"*{route['en']}*"
                    
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #e0e0e0;
                        border-radius: 10px;
                        padding: 12px;
                        margin: 5px 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        transition: transform 0.2s;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    ">
                        <div style="text-align: center; color: white;">
                            {card_title}<br>
                            <span style="font-size: 0.85em;">{card_subtitle}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 关键修改：按钮点击后只显示对应语言的解释
                    if st.button(f"📖 View" if language == "English" else f"📖 查看详情", key=f"route_card_{route['en']}_{idx}", use_container_width=True):
                        if language == "English":
                            # 只显示英文
                            st.info(f"""
                            ### {route['en']}
                            
                            **📝 Description:**  
                            {route['desc_en']}
                            
                            **🏷️ Category:** {category_names.get(route['category'], route['category'])}
                            """)
                        else:
                            # 只显示中文
                            st.info(f"""
                            ### {route['zh']}
                            
                            **📖 说明：**  
                            {route['desc_zh']}
                            
                            **🏷️ 分类：** {route['category']}
                            """)
    
    st.markdown("---")
    if language == "English":
        st.caption(f"✅ Total {len(route_reference)} routes | Showing {len(filtered_routes)}")
    else:
        st.caption(f"✅ 共 {len(route_reference)} 条路线 | 当前显示 {len(filtered_routes)} 条")


@st.cache_data(ttl=3600, show_spinner=False)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_phase2(candidate_names: tuple, user_text: str, extracted_weakness: str,
                  preference: str, language: str):
    """
    第二阶段：从候选中精选最佳战术
    candidate_names 需要转为 tuple（可哈希）
    """
    desc = get_full_desc(list(candidate_names))
    weak_ctx = f"\n\nAI extracted weakness tags: {extracted_weakness}" if extracted_weakness else ""

    user_preference = ""
    if preference == "优先安全战术（高成功率，短传为主）":
        user_preference = "请注意：用户偏好安全、高成功率的短传战术。"
    elif preference == "优先激进战术（深远打击，风险高！！！）":
        user_preference = "请注意：用户偏好激进、能快速推进的深远战术。"
    if language == "English":
        if preference == "Safe (highly short passes safe but might not be effective)":
            user_preference = "Note: User prefers safe, high-percentage short passes."
        elif preference == "Aggressive (normally deep strikes，risky!!!)":
            user_preference = "Note: User prefers aggressive, deep-strike tactics."

    if language == "English":
        output_format = """
You MUST respond in English using EXACTLY this format. Do not use Chinese.

🏆 **Best Tactic:** [tactic name from candidates]
📝 **Why this tactic:** [2-3 sentences explaining the choice based on the game situation]
⚡ **Key execution points:** [what to pay attention to when running this play]
📊 **Expected result:** [estimated yardage gain or success rate]

🔄 **Backup tactic:** [alternative tactic name from candidates]
🔀 **When to switch:** [under what circumstances to use the backup instead]
"""
    else:
        output_format = """
你必须用中文回答，严格按照以下格式：

🏆 **最佳战术：** [从候选中选出的战术名]
📝 **推荐理由：** [2-3句话解释为什么选这个战术]
⚡ **执行要点：** [执行这个战术时需要注意的关键点]
📊 **预估效果：** [预计推进码数或成功率]

🔄 **备选战术：** [从候选中选出的备选战术名]
🔀 **切换时机：** [什么情况下应该改用备选战术]
"""

    prompt2 = f"""
你是一名精通5v5腰旗橄榄球的战术教练。你的任务是从以下候选战术中选出1个最适合当前比赛的最佳战术，以及1个备选战术。

【候选战术详情】
{desc}

【用户描述的比赛情况】
{user_text}{weak_ctx}

{user_preference if user_preference else ""}

{output_format}

重要：你只能从上述候选战术中选择，绝对不能自己编造战术。如果用户的描述和任何战术都不完全匹配，请选择最接近的那个并说明理由。
"""
    max_retries2 = 2
    for attempt2 in range(max_retries2 + 1):
        try:
            response2 = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一名专业的腰旗橄榄球战术教练。你只能从提供的候选战术中选择，绝不编造战术。You must follow the output format exactly."},
                    {"role": "user", "content": prompt2}
                ],
                temperature=0.6,
                max_tokens=450
            )
            return response2.choices[0].message.content
        except openai.RateLimitError as e:
            if attempt2 < max_retries2:
                time.sleep((attempt2 + 1) * 3)
            else:
                raise e
        except openai.AuthenticationError as e:
            raise e
        except openai.APIConnectionError as e:
            if attempt2 < max_retries2:
                time.sleep(2)
            else:
                raise e
        except openai.APITimeoutError as e:
            if attempt2 < max_retries2:
                time.sleep(2)
            else:
                raise e
        except openai.BadRequestError as e:
            raise e
        except Exception as e:
            if attempt2 < max_retries2:
                time.sleep(2)
            else:
                raise e
# ==================== 战术动态可视化模块 ====================
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import FancyBboxPatch
import numpy as np
from io import BytesIO
from PIL import Image

# ---------- 球场绘制参数 ----------
FIELD_LENGTH = 100   # 码
FIELD_WIDTH = 53.3   # 码
# 绘图坐标：x 代表从本方端区到对方端区，y 代表宽度
# 为了方便，我们以场地左下角为(0,0)，右上角为(FIELD_LENGTH, FIELD_WIDTH)

def draw_field(ax):
    """绘制简化橄榄球场"""
    ax.set_xlim(-5, FIELD_LENGTH + 5)
    ax.set_ylim(-5, FIELD_WIDTH + 5)
    ax.set_facecolor('#2E7D32')  # 绿茵
    # 码线
    for yd in range(0, 101, 10):
        ax.axvline(x=yd, color='white', linewidth=1, alpha=0.3)
        ax.text(yd, -2, str(yd), ha='center', color='white', fontsize=6)
    # 边线
    ax.plot([0, FIELD_LENGTH], [0, 0], color='white', linewidth=2)
    ax.plot([0, FIELD_LENGTH], [FIELD_WIDTH, FIELD_WIDTH], color='white', linewidth=2)
    # 端区
    ax.axvline(x=0, color='white', linewidth=3)
    ax.axvline(x=FIELD_LENGTH, color='white', linewidth=3)
    ax.axis('off')

# ---------- 路线形状定义（相对坐标）----------
# 每条路线给出从起点开始的路径点序列（码），起点位置由球员类型决定
ROUTE_SHAPES = {
    "Fly": [(0,0), (20,0), (40,0)],                      # 垂直冲刺
    "Hitch": [(0,0), (6,0), (6,2)],                       # 前冲6码回身
    "Slant": [(0,0), (3,2), (6,4), (9,6)],               # 45度内切
    "Out": [(0,0), (5,0), (7,-3), (10,-5)],              # 外直角
    "In": [(0,0), (5,0), (7,3), (10,5)],                 # 内直角
    "Post": [(0,0), (8,0), (12,3), (16,6)],              # 内切45度
    "Corner": [(0,0), (8,0), (12,-3), (16,-6)],          # 外切45度
    "Post-Corner": [(0,0), (6,2), (10,0), (14,-4)],      # 先内后外
    "Corner-Post": [(0,0), (6,-2), (10,0), (14,4)],      # 先外后内
    "Stop and Go": [(0,0), (6,0), (6,1), (20,0)],        # 急停再启动
    "Chair": [(0,0), (4,0), (4,-4), (20,-4)],            # 横向再垂直
    "Option": [(0,0), (5,2), (8,2)],                      # 简化为斜插
    "Curl": [(0,0), (8,0), (8,-3), (10,-3)],             # 弧线回身
    "Comeback": [(0,0), (12,0), (12,3), (15,2)],         # 深回退
    "Whip": [(0,0), (5,2), (8,0), (10,-3)],              # 鞭打
    "Dig": [(0,0), (8,0), (12,4), (12,6)],               # 深凿内切
    "Fade": [(0,0), (20,-4), (30,-8)],                    # 边线高球
    "Flat": [(0,0), (3,-2), (5,-4)],                      # 坪区
    "Wheel": [(0,0), (3,-4), (20,-4)],                    # 车轮
    "Drag": [(0,0), (2,0), (10,0), (20,2)],               # 横穿（简化）
    "Snag": [(0,0), (3,0), (3,2)],                        # 短斜
    "Stick": [(0,0), (4,0), (4,-2)],                      # 棍棒
    "Juke": [(0,0), (2,1), (2,-1), (8,0)],               # 晃动
    "Seam": [(0,0), (15,0), (20,0)],                      # 接缝垂直
    "Speed Out": [(0,0), (12,0), (14,-4), (16,-6)],      # 快速外切
}

# 常用简写映射（战术描述中可能出现的变体）
ROUTE_ALIASES = {
    "飞驰路线": "Fly", "回身路线": "Hitch", "斜插路线": "Slant",
    "外侧直角路线": "Out", "内侧直角路线": "In", "柱状路线": "Post",
    "底角路线": "Corner", "柱角假动作路线": "Post-Corner",
    "角柱假动作路线": "Corner-Post", "急停再启动路线": "Stop and Go",
    "座椅路线": "Chair", "选项路线": "Option", "卷曲路线": "Curl",
    "回退长路线": "Comeback", "鞭打路线": "Whip", "深凿路线": "Dig",
    "高弧深远路线": "Fade", "坪区路线": "Flat", "车轮路线": "Wheel",
    "拖拽横穿路线": "Drag", "斯纳格路线": "Snag", "棍棒路线": "Stick",
    "晃动路线": "Juke", "接缝路线": "Seam", "速度外切": "Speed Out",
    # 英文别名
    "Fly Route": "Fly", "Hitch Route": "Hitch", "Slant Route": "Slant",
    "Out Route": "Out", "In Route": "In", "Post Route": "Post",
    "Corner Route": "Corner", "Post-Corner Route": "Post-Corner",
    "Corner-Post Route": "Corner-Post", "Stop and Go Route": "Stop and Go",
    "Chair Route": "Chair", "Option Route": "Option", "Curl Route": "Curl",
    "Comeback Route": "Comeback", "Whip Route": "Whip", "Dig Route": "Dig",
    "Fade Route": "Fade", "Flat Route": "Flat", "Wheel Route": "Wheel",
    "Drag Route": "Drag", "Snag Concept": "Snag", "Stick Concept": "Stick",
    "Juke": "Juke", "Seam Route": "Seam", "Speed Out": "Speed Out",
}

# 球员初始站位（x, y）码，x为纵向位置（距启球线），y为横向位置（码线宽度）
# 我们假设进攻方向为x正方向，启球线在x=20码处
LOS = 20  # line of scrimmage
PLAYER_POSITIONS = {
    "QB": (15, FIELD_WIDTH/2),
    "C": (20, FIELD_WIDTH/2),
    "RB": (16, FIELD_WIDTH/2 + 5),
    "左侧WR": (20, 5),
    "右侧WR": (20, FIELD_WIDTH - 5),
    "Slot": (20, FIELD_WIDTH/2 + 2),
    "槽位": (20, FIELD_WIDTH/2 + 2),
    "槽位Slot": (20, FIELD_WIDTH/2 + 2),
    "远端Slot": (20, FIELD_WIDTH - 2),
    "左侧槽位": (20, 8),
    "右侧槽位": (20, FIELD_WIDTH - 8),
    "近端锋": (20, FIELD_WIDTH/2 + 2),
    "左外接": (20, 5),
    "右外接": (20, FIELD_WIDTH - 5),
    "外侧WR": (20, 5),   # 默认左侧
    "最外侧WR": (20, 5),
}

def parse_tactic_description(desc):
    """
    从战术中文描述中提取球员->路线映射。
    返回列表：[(球员中文名, 路线英文名, 球员位置坐标), ...]
    """
    assignments = []
    # 模式1：左侧WR / 右侧WR / Slot / RB 等 + 跑 + 路线名
    # 匹配 "左侧WR跑Fly路线"、"右侧WR跑Post路线"、"Slot跑Slant路线"
    pattern1 = r'(左侧WR|右侧WR|槽位Slot|Slot|RB|左侧槽位|右侧槽位|左外接|右外接|外侧WR|最外侧WR|C|QB|远端Slot|近端锋)\s*跑\s*(\S+路线)'
    matches1 = re.findall(pattern1, desc)
    for player, route_name in matches1:
        route_en = ROUTE_ALIASES.get(route_name, None)
        if not route_en:
            # 尝试去掉“路线”二字再匹配
            route_en = ROUTE_ALIASES.get(route_name.replace("路线", ""), None)
        if route_en:
            pos = PLAYER_POSITIONS.get(player, (20, FIELD_WIDTH/2 + 2))
            assignments.append((player, route_en, pos))
    
    # 模式2：QB...后撤，不画路线；C开球后释放跑...路线
    pattern2 = r'C开球后.*?释放.*?跑\s*(\S+路线)'
    match_c = re.search(pattern2, desc)
    if match_c:
        route_name = match_c.group(1)
        route_en = ROUTE_ALIASES.get(route_name, ROUTE_ALIASES.get(route_name.replace("路线",""), None))
        if route_en:
            assignments.append(("C", route_en, PLAYER_POSITIONS["C"]))
    
    # 模式3：英文描述中的类似模式
    # 可扩展，目前先覆盖中文为主
    return assignments

def generate_tactic_gif(tactic_name):
    """生成战术动画GIF并返回BytesIO对象"""
    tactic = next((t for t in tactics_full if t['name'] == tactic_name), None)
    if not tactic:
        return None
    desc = tactic['desc']
    assignments = parse_tactic_description(desc)
    if not assignments:
        return None

    # 创建画布
    fig, ax = plt.subplots(figsize=(8, 5))
    draw_field(ax)
    ax.set_title(tactic_name, color='white', fontsize=12)

    # 初始化球员点
    player_dots = {}
    for player, route, (x0, y0) in assignments:
        dot, = ax.plot([], [], 'o', color='white', markersize=8, zorder=5)
        # 路线线段
        line, = ax.plot([], [], color='yellow', linewidth=2, zorder=4)
        player_dots[player] = {'dot': dot, 'line': line, 'route': route, 'start': (x0, y0)}
    
    # 获取每条路线的路径点序列（基于起点）
    route_points_cache = {}
    for player, data in player_dots.items():
        shape = ROUTE_SHAPES.get(data['route'], [(0,0)])
        start_x, start_y = data['start']
        pts = [(start_x + dx, start_y + dy) for dx, dy in shape]
        route_points_cache[player] = pts

    total_frames = 50  # 动画帧数
    def animate(frame):
        progress = frame / total_frames
        for player, data in player_dots.items():
            pts = route_points_cache[player]
            if len(pts) < 2:
                continue
            # 计算当前已走完的路径比例对应的点
            total_len = 0
            segments = []
            for i in range(len(pts)-1):
                seg_len = np.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1])
                segments.append(seg_len)
                total_len += seg_len
            target_len = progress * total_len
            cum_len = 0
            cut_point = None
            for i, seg_len in enumerate(segments):
                if cum_len + seg_len >= target_len:
                    frac = (target_len - cum_len) / seg_len
                    cut_point = (pts[i][0] + frac*(pts[i+1][0]-pts[i][0]),
                                 pts[i][1] + frac*(pts[i+1][1]-pts[i][1]))
                    break
                cum_len += seg_len
            if cut_point is None:
                cut_point = pts[-1]
            # 更新圆点位置
            data['dot'].set_data([cut_point[0]], [cut_point[1]])
            # 更新已画路线
            line_x = [pts[0][0]]
            line_y = [pts[0][1]]
            cum = 0
            for i, seg_len in enumerate(segments):
                if cum + seg_len >= target_len:
                    frac = (target_len - cum) / seg_len
                    line_x.append(pts[i][0] + frac*(pts[i+1][0]-pts[i][0]))
                    line_y.append(pts[i][1] + frac*(pts[i+1][1]-pts[i][1]))
                    break
                cum += seg_len
                line_x.append(pts[i+1][0])
                line_y.append(pts[i+1][1])
            data['line'].set_data(line_x, line_y)
        return []

    ani = animation.FuncAnimation(fig, animate, frames=total_frames, interval=50, blit=False)
    
    # 保存为GIF到BytesIO
    gif_buffer = BytesIO()
    ani.save(gif_buffer, writer='pillow', fps=10)
    plt.close(fig)
    gif_buffer.seek(0)
    return gif_buffer

# 将所有战术名列表供下拉菜单使用
tactic_names_for_viz = [t['name'] for t in tactics_full]
with st.expander("🎬 战术动态演示" if language == "中文" else "🎬 Dynamic Tactic Demo", expanded=False):
    selected_tactic = st.selectbox(
        "选择战术查看动画" if language == "中文" else "Select a tactic to view animation",
        tactic_names_for_viz,
        key="tactic_viz"
    )
    if st.button("▶️ 播放动画" if language == "中文" else "▶️ Play Animation", key="play_viz"):
        with st.spinner("生成动画中..." if language == "中文" else "Generating animation..."):
            gif_buffer = generate_tactic_gif(selected_tactic)
            if gif_buffer:
                st.image(gif_buffer, caption=selected_tactic, use_container_width=True)
            else:
                st.warning("该战术暂无可视化数据，请选择其他战术。" if language == "中文" else "No visualization available for this tactic.")

# ==================== AI 两阶段筛选 ====================
st.subheader("🧠动态战术筛选" if language == "中文" else "🧠Dynamic Tactical Analysis")

if st.button(L["button"], type="primary"):

    # ===== 调试模式：直接返回模拟结果 =====
    if DEBUG_MODE:
        st.info("🔧 调试模式：AI 分析功能暂未启用")
        st.markdown("""
        ### 📋 模拟推荐结果
        
        🏆 **最佳战术：** 飞驰路线 (Fly Route)  
        📝 **推荐理由：** 对方安全卫站位过深，深远路线有大量空间可以利用  
        ⚡ **执行要点：** QB三步后撤，左侧WR全速冲刺30码以上，注意口袋保护  
        📊 **预估效果：** 预计推进25-30码，有达阵可能  
        
        🔄 **备选战术：** 高弧深远路线 (Fade Route)  
        🔀 **切换时机：** 当对方角卫身高不占优势时，可改用Fade争顶
        
        ---
        ⚠️ 正式使用时，请将代码开头的 `DEBUG_MODE = False` 并配置 API Key
        """)
        st.session_state.query_count += 1
        st.stop()
    
    # ===== 以下是正式 AI 调用（DEBUG_MODE=False 时执行）=====

    if not free_text.strip():
        st.warning(L["warn"])
        st.stop()

    user_preference = ""
    if need_quick == L["pref_opts"][1]:
        user_preference = "Note: User prefers safe, high-percentage short passes." if language == "English" else "请注意：用户偏好安全、高成功率的短传战术。"
    elif need_quick == L["pref_opts"][2]:
        user_preference = "Note: User prefers aggressive, deep-strike tactics." if language == "English" else "请注意：用户偏好激进、能快速推进的深远战术。"
    
    # ===== 第一阶段 =====
    with st.spinner(L["spinner1"]):
        prompt1 = f"""
你是一名腰旗橄榄球战术分析师。
任务：
1. 从【可用弱点标签库】中找出用户描述里的对方弱点（最多3个）。
2. 根据弱点从【战术索引】中选最相关的5-6条战术。

【可用弱点标签库】
{all_tags_string}

【战术索引】
{index_text}

【用户描述】
{free_text}

{user_preference if user_preference else ""}

{L["lang_instr"]}

格式：
弱点提取：标签1，标签2，...
候选战术：
战术名1
战术名2
...
"""
        r1 = None
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                r1 = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "Strict format: weakness extraction then candidate tactics."},
                        {"role": "user", "content": prompt1}
                    ],
                    temperature=0.3, max_tokens=300
                )
                break
            except openai.RateLimitError as e:
                if attempt < max_retries:
                    wait_time = (attempt + 1) * 3
                    st.warning(f"⏳ API 请求频率过高，{wait_time}秒后重试 ({attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    st.error(f"❌ API 额度用尽或请求过于频繁。请稍后再试。\n错误详情：{e}")
                    st.stop()
            
            except openai.AuthenticationError as e:
                st.error(f"🔑 API Key 无效或已过期。\n错误详情：{e}")
                st.stop()
            
            except openai.APIConnectionError as e:
                if attempt < max_retries:
                    st.warning(f"🌐 网络连接失败，正在重试 ({attempt+1}/{max_retries})...")
                    time.sleep(2)
                else:
                    st.error(f"🌐 无法连接到 OpenAI 服务器。\n错误详情：{e}")
                    st.stop()
            
            except openai.APITimeoutError as e:
                if attempt < max_retries:
                    st.warning(f"⏰ 请求超时，正在重试 ({attempt+1}/{max_retries})...")
                    time.sleep(2)
                else:
                    st.error(f"⏰ 请求超时。\n错误详情：{e}")
                    st.stop()
            
            except openai.BadRequestError as e:
                st.error(f"📝 请求格式有误。\n错误详情：{e}")
                st.stop()
            
            except Exception as e:
                if attempt < max_retries:
                    st.warning(f"⚠️ 未知错误，正在重试 ({attempt+1}/{max_retries})...")
                    time.sleep(2)
                else:
                    st.error(f"❌ {L['error2']}\n错误类型：{type(e).__name__}\n错误详情：{e}")
                    st.stop()

        raw = r1["choices"][0]["message"]["content"].strip()
        lines = raw.split("\n")
        extracted, candidates = "", []
        found = False
        for line in lines:
            line = line.strip()
            if line.startswith("弱点提取：") or line.startswith("弱点提取:"):
                extracted = line.split("：")[-1].split(":")[-1].strip()
                found = True
            elif found and line and "候选战术" not in line:
                candidates.append(line.strip())
        if not candidates:
            candidates = [l.strip() for l in lines if l.strip() and "弱点" not in l]

        if not candidates:
            st.error(L["error1"])
            st.stop()

        if extracted:
            st.success(f"{L['weak_found']}**{extracted}**")
        else:
            st.info(L["weak_none"])
        st.info(L["cand_found"].format(len(candidates)) + f": {', '.join(candidates[:6])}")

    # ===== 第二阶段：精选 =====
    with st.spinner(L["spinner2"]):
        try:
            final_output = cached_phase2(
                tuple(candidates),
                free_text,
                extracted,
                need_quick,
                language
            )
        except Exception as e:
            st.error(f"❌ {L['error3']}\n{e}")
            st.stop()
        desc = get_full_desc(candidates)
        weak_ctx = f"\n\nAI extracted weakness tags: {extracted}" if extracted else ""

        if language == "English":
            output_format = """
You MUST respond in English using EXACTLY this format. Do not use Chinese.

🏆 **Best Tactic:** [tactic name from candidates]
📝 **Why this tactic:** [2-3 sentences explaining the choice based on the game situation]
⚡ **Key execution points:** [what to pay attention to when running this play]
📊 **Expected result:** [estimated yardage gain or success rate]

🔄 **Backup tactic:** [alternative tactic name from candidates]
🔀 **When to switch:** [under what circumstances to use the backup instead]
"""
        else:
            output_format = """
你必须用中文回答，严格按照以下格式：

🏆 **最佳战术：** [从候选中选出的战术名]
📝 **推荐理由：** [2-3句话解释为什么选这个战术]
⚡ **执行要点：** [执行这个战术时需要注意的关键点]
📊 **预估效果：** [预计推进码数或成功率]

🔄 **备选战术：** [从候选中选出的备选战术名]
🔀 **切换时机：** [什么情况下应该改用备选战术]
"""

        prompt2 = f"""
你是一名精通5v5腰旗橄榄球的战术教练。你的任务是从以下候选战术中选出1个最适合当前比赛的最佳战术，以及1个备选战术。

【候选战术详情】
{desc}

【用户描述的比赛情况】
{free_text}{weak_ctx}

{user_preference if user_preference else ""}

{output_format}

重要：你只能从上述候选战术中选择，绝对不能自己编造战术。如果用户的描述和任何战术都不完全匹配，请选择最接近的那个并说明理由。
"""
        response2 = None
        max_retries2 = 2
        for attempt2 in range(max_retries2 + 1):
            try:
                response2 = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "你是一名专业的腰旗橄榄球战术教练。你只能从提供的候选战术中选择，绝不编造战术。You must follow the output format exactly."},
                        {"role": "user", "content": prompt2}
                    ],
                    temperature=0.6,
                    max_tokens=450
                )
                break
            except openai.RateLimitError as e:
                if attempt2 < max_retries2:
                    wait_time = (attempt2 + 1) * 3
                    st.warning(f"⏳ API 请求频率过高，{wait_time}秒后重试 ({attempt2+1}/{max_retries2})...")
                    time.sleep(wait_time)
                else:
                    st.error(f"❌ API 额度用尽或请求过于频繁。请稍后再试。\n错误详情：{e}")
                    st.stop()
            
            except openai.AuthenticationError as e:
                st.error(f"🔑 API Key 无效。\n错误详情：{e}")
                st.stop()
            
            except openai.APIConnectionError as e:
                if attempt2 < max_retries2:
                    st.warning(f"🌐 网络连接失败，正在重试 ({attempt2+1}/{max_retries2})...")
                    time.sleep(2)
                else:
                    st.error(f"🌐 无法连接到 OpenAI 服务器。\n错误详情：{e}")
                    st.stop()
            
            except openai.APITimeoutError as e:
                if attempt2 < max_retries2:
                    st.warning(f"⏰ 请求超时，正在重试 ({attempt2+1}/{max_retries2})...")
                    time.sleep(2)
                else:
                    st.error(f"⏰ 请求超时。\n错误详情：{e}")
                    st.stop()
            
            except openai.BadRequestError as e:
                st.error(f"📝 请求格式有误。\n错误详情：{e}")
                st.stop()
            
            except Exception as e:
                if attempt2 < max_retries2:
                    st.warning(f"⚠️ 未知错误，正在重试 ({attempt2+1}/{max_retries2})...")
                    time.sleep(2)
                else:
                    st.error(f"❌ {L['error3']}\n错误类型：{type(e).__name__}\n错误详情：{e}")
                    st.stop()

        final_output = response2.choices[0].message.content
        st.success(L["done"])
        st.session_state.query_count += 1
        st.markdown("---")
        st.markdown(final_output)

        # 下载按钮
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download recommendation" if language == "English" else "📥 下载推荐结果",
                data=final_output,
                file_name=f"tactic_recommendation.txt",
                mime="text/plain"
            )