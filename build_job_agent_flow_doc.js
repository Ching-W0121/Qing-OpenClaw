const fs = require('fs');
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
  AlignmentType,
  LevelFormat,
  Header,
  Footer,
  PageNumber,
} = require('docx');

const outPath = 'C:/Users/TR/Desktop/求职Agent运行流程说明.docx';

const bullet = (text) => new Paragraph({
  numbering: { reference: 'bullet-list', level: 0 },
  children: [new TextRun({ text, font: 'Arial' })],
});

const num1 = (text) => new Paragraph({
  numbering: { reference: 'num-main', level: 0 },
  children: [new TextRun({ text, font: 'Arial' })],
});

const para = (text) => new Paragraph({
  children: [new TextRun({ text, font: 'Arial' })],
  spacing: { after: 120 },
});

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: 'Arial', size: 24 },
      },
    },
    paragraphStyles: [
      {
        id: 'Title',
        name: 'Title',
        basedOn: 'Normal',
        run: { font: 'Arial', size: 36, bold: true, color: '000000' },
        paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 240, after: 240 } },
      },
      {
        id: 'Heading1',
        name: 'Heading 1',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { font: 'Arial', size: 30, bold: true, color: '000000' },
        paragraph: { spacing: { before: 240, after: 180 }, outlineLevel: 0 },
      },
      {
        id: 'Heading2',
        name: 'Heading 2',
        basedOn: 'Normal',
        next: 'Normal',
        quickFormat: true,
        run: { font: 'Arial', size: 26, bold: true, color: '000000' },
        paragraph: { spacing: { before: 180, after: 120 }, outlineLevel: 1 },
      },
    ],
  },
  numbering: {
    config: [
      {
        reference: 'bullet-list',
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: '•',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
      {
        reference: 'num-main',
        levels: [
          {
            level: 0,
            format: LevelFormat.DECIMAL,
            text: '%1.',
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } },
          },
        ],
      },
    ],
  },
  sections: [{
    properties: {
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
    },
    headers: {
      default: new Header({
        children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '求职 Agent 运行流程说明', font: 'Arial', size: 18 })] })],
      }),
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'Page ', font: 'Arial' }), new TextRun({ children: [PageNumber.CURRENT] }), new TextRun({ text: ' / ', font: 'Arial' }), new TextRun({ children: [PageNumber.TOTAL_PAGES] })] })],
      }),
    },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun('求职 Agent 运行流程说明')] }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '版本：当前运行框架复述版', font: 'Arial', size: 22 })], spacing: { after: 240 } }),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('一、系统定位')] }),
      para('这套求职 Agent 不是简单的自动投递脚本，而是一套围绕“岗位召回、筛选、评分、去重、投递、验证、记录、汇报”展开的求职执行系统。它的目标不是盲目提高投递数量，而是尽量只投真正匹配、值得投、风险可控的岗位。'),
      bullet('核心目标：精准投递，而不是脏投、乱投、重复投。'),
      bullet('核心方向：品牌策划、品牌宣传、品牌设计、视觉设计等相关岗位。'),
      bullet('核心原则：先判断该不该投，再决定要不要投。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('二、系统整体分层')] }),
      para('目前整套求职 Agent 可以理解为以下几个连续层级：'),
      num1('目标配置层：定义用户画像、岗位方向、城市范围、薪资底线、经验边界。'),
      num1('职位召回层：从各招聘平台按目标方向搜索并拉回岗位。'),
      num1('岗位清洗与标准化层：把不同平台的岗位统一成同一结构。'),
      num1('详情页补全层：进入职位详情页补足职责、要求、行业与真实信息。'),
      num1('硬过滤层：先筛掉明确不该投的岗位。'),
      num1('动态评分层：对可投岗位进行优先级排序。'),
      num1('去重层：避免重复抓取、重复推荐、重复投递。'),
      num1('候选池与投递桶层：把岗位分为立即投递、暂缓观察、明确放弃。'),
      num1('投递执行层：进入真实详情页完成投递动作。'),
      num1('状态验证层：通过页面状态变化确认是否真实投递成功。'),
      num1('结果记录与汇报层：把每轮执行结果整理成结构化输出。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('三、目标配置层')] }),
      para('系统每次运行前，首先基于用户当前求职目标建立本轮执行画像。这个画像决定了系统会找什么岗位、在哪找、什么条件下可以投。'),
      bullet('目标岗位族：品牌策划、品牌宣传、品牌设计、视觉设计等。'),
      bullet('目标城市：深圳。'),
      bullet('排除区域：宝安区。'),
      bullet('薪资下限：至少 8K，优先 10K-15K。'),
      bullet('经验边界：以 1-5 年为主，明显过高岗位要谨慎或直接拦截。'),
      bullet('行业与职责偏好：优先真正与品牌表达、品牌传播、品牌视觉相关的岗位。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('四、职位召回层')] }),
      para('系统会按平台和岗位方向制定搜索计划，再根据主关键词和少量相关词进行职位召回。这里的重点不是无限扩展关键词，而是在保证方向准确的前提下，提高有效岗位的覆盖率。'),
      bullet('主攻平台：智联招聘、前程无忧（51job）、猎聘。'),
      bullet('搜索依据：岗位方向 + 关键词组合。'),
      bullet('正确策略：主关键词优先，相关词适度补充，不为了扩大召回而污染岗位边界。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('五、岗位清洗与标准化层')] }),
      para('不同平台返回的岗位字段结构不同，因此系统会先做统一标准化。标准化后，后续判断逻辑不再依赖平台原始页面，而是依赖统一后的岗位对象。'),
      bullet('统一字段通常包括：公司、岗位名称、薪资、地点、经验、学历、岗位描述、技能要求、行业标签、详情页入口、平台来源。'),
      bullet('标准化的意义：为后续评分、过滤、投递提供统一输入。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('六、详情页补全层')] }),
      para('系统不会只凭搜索列表页信息直接决定是否投递，而是优先使用岗位详情页入口来补齐真实信息。详情页是整个求职 Agent 的业务真入口。'),
      bullet('列表页信息通常不完整，只适合初步召回，不适合最终决策。'),
      bullet('详情页可补足岗位职责、经验要求、行业属性、真实工作内容等关键信息。'),
      bullet('详情页也是最适合执行投递动作与验证投递状态的页面。'),
      bullet('整个主线应以详情页入口为准，而不是旧链接、模糊链接或缓存入口。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('七、硬过滤层')] }),
      para('硬过滤层负责拦截“明确不该投”的岗位。也就是说，只要某个岗位在确定性条件上不符合要求，就直接退出，不进入后续评分。'),
      bullet('区域不符：如宝安区岗位直接排除。'),
      bullet('薪资不达标：明显低于底线的岗位直接排除。'),
      bullet('经验要求过高：如明显属于 5-10 年高阶岗位，直接拦截。'),
      bullet('岗位级别过高：总监级、负责人级、高管级岗位直接排除。'),
      bullet('岗位族不匹配：销售、运营、推广、商务拓展等混入岗位直接排除。'),
      bullet('缺少有效详情入口或核心字段严重缺失的岗位，不进入真实投递流程。'),
      para('这一层的原则是：确定性不匹配的问题，不交给后面的动态评分去模糊兜底。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('八、动态评分层')] }),
      para('硬过滤通过之后，岗位才会进入动态评分层。评分的目的不是决定“所有岗位能不能投”，而是对已经基本合格的岗位做优先级排序。'),
      bullet('常见评分维度：岗位匹配度、薪资契合度、地点契合度、关键词相关度、行业相关度。'),
      bullet('评分输出的意义：决定哪些岗位优先投，哪些岗位先保留观察。'),
      bullet('正确顺序：先 hard gate，再 scoring。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('九、去重层')] }),
      para('求职系统如果缺少去重，最终会导致重复抓取、重复推荐、重复投递。因此去重是整个运行流程里的关键基础能力。'),
      bullet('搜索结果去重：同平台同岗位多次出现时，只保留一份。'),
      bullet('跨关键词去重：同一个岗位可能会被多个关键词同时召回。'),
      bullet('跨轮次去重：避免昨天投过、今天又重复进入候选池。'),
      bullet('投递记录去重：已投递岗位不能再被重新投递。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十、候选池与投递桶')] }),
      para('经过清洗、补全、过滤、评分和去重后，岗位会进入候选池，再按执行优先级分流。不是所有通过筛选的岗位都要立即投递。'),
      bullet('立即投递：符合当前标准，且优先级足够高。'),
      bullet('暂缓观察：基本合格，但当前不急于投递。'),
      bullet('明确放弃：虽被召回，但最终判定不值得投。'),
      para('这个阶段的本质，是把岗位从“可看”进一步收缩到“可投”。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十一、投递执行层')] }),
      para('当岗位进入立即投递桶后，系统才会进入真实执行阶段。执行阶段必须围绕详情页进行，而不是在模糊页面上做假动作。'),
      bullet('进入真实详情页。'),
      bullet('确认当前页面状态：可投递、已投递、不可投、页面异常、登录失效等。'),
      bullet('仅对明确可投的岗位执行动作。'),
      bullet('动作执行后，重新获取页面状态。'),
      para('动态网页执行的关键原则是：不能复用旧页面元素，不能用旧状态假设成功，必须在动作后重新检查页面。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十二、状态验证层')] }),
      para('投递动作完成后，系统不能仅凭“函数结束”或“页面打开成功”就判定 submitted，而必须依赖真实状态变化。'),
      bullet('强验证信号：按钮从“立即投递”变为“已投递”；页面明确显示“已申请”；平台状态变为 submitted 或 already_applied。'),
      bullet('弱验证信号不能单独作为成功依据：仅打开页面、仅点击动作返回、仅等待后主观判定成功。'),
      bullet('没有真实状态变化的 submitted，不算真正成功。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十三、结果记录层')] }),
      para('一旦投递结果得到验证，系统就会把业务结果沉淀下来，供后续去重、统计与汇报使用。这里记录的不是简单的“投了没”，而是整个投递状态。'),
      bullet('记录对象包括：用户、岗位、平台、投递时间、投递状态、详情页入口、原因说明。'),
      bullet('常见状态：submitted、already_applied、failed、rejected。'),
      bullet('记录必须具备幂等性：同一岗位不能因为重跑而产生多条重复投递记录。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十四、结果汇报层')] }),
      para('每轮运行结束后，系统应输出结构化结果，而不是只返回一句“完成”。汇报的重点是把搜索、筛选、投递、失败原因与最终结论讲清楚。'),
      bullet('本轮搜索了哪些平台、哪些方向、哪些关键词。'),
      bullet('召回了多少岗位，多少进入有效候选。'),
      bullet('多少岗位被硬过滤拦截，分别因为什么被拒绝。'),
      bullet('多少岗位进入立即投递，多少暂缓，多少放弃。'),
      bullet('本轮真实 submitted、already_applied、failed 的数量。'),
      bullet('若有失败，必须说明失败点在搜索、详情补全、执行还是验证环节。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十五、用户交付层')] }),
      para('最终交付给用户的结果，不应只是内部状态或原始 JSON，而应是可直接阅读和决策的结构化输出。岗位不仅要被找到和投递，还要被解释清楚。'),
      bullet('交付重点包括：为什么这个岗位值得投。'),
      bullet('交付重点包括：为什么某个岗位不投。'),
      bullet('交付重点包括：当前平台链路是否可靠。'),
      bullet('交付重点包括：本轮行动带来了哪些真实结果。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十六、标准运行顺序（总流程复述）')] }),
      num1('读取用户求职画像。'),
      num1('制定本轮平台与关键词搜索计划。'),
      num1('从平台召回岗位。'),
      num1('对岗位做统一清洗与标准化。'),
      num1('优先进入详情页补全真实信息。'),
      num1('先做硬过滤，剔除确定性不匹配岗位。'),
      num1('再做动态评分，对合格岗位排序。'),
      num1('执行去重，排除重复岗位与历史已投岗位。'),
      num1('把岗位分流进立即投递、暂缓观察、明确放弃三个桶。'),
      num1('对立即投递岗位进入详情页执行真实投递动作。'),
      num1('动作后重新检查页面状态，验证是否 submitted 或 already_applied。'),
      num1('把业务结果记录下来，用于后续去重、统计和汇报。'),
      num1('输出本轮结构化汇报，明确结果、原因和下一步方向。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十七、整套系统的核心原则')] }),
      bullet('宁可少投，也不乱投。'),
      bullet('详情页是真入口，列表页只适合召回。'),
      bullet('先硬过滤，再评分。'),
      bullet('没有真实状态变化，就不算 submitted。'),
      bullet('去重必须贯穿搜索、候选、投递三层。'),
      bullet('每轮输出必须能回答：找了什么、为什么投、为什么不投、结果是否真实。'),

      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun('十八、当前框架的一句话总结')] }),
      para('这套求职 Agent 的完整设计，本质上是一条“目标定义 → 岗位召回 → 信息补全 → 硬过滤 → 动态评分 → 去重分流 → 详情页投递 → 状态验证 → 结果记录 → 用户汇报”的业务闭环。它追求的不是机械自动化，而是可控、可解释、可复用的精准投递流程。'),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outPath, buffer);
  console.log(`DOCX_CREATED:${outPath}`);
}).catch((err) => {
  console.error(err);
  process.exit(1);
});
