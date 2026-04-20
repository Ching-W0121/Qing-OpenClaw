const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, LevelFormat, ExternalHyperlink, HeadingLevel,
        BorderStyle, WidthType, ShadingType, VerticalAlign, PageBreak,
        PageOrientation, UnderlineType } = require('docx');
const fs = require('fs');

// ==================== 创建文档 ====================
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 24 }
      }
    },
    paragraphStyles: [
      {
        id: "Title",
        name: "Title",
        basedOn: "Normal",
        run: { size: 56, bold: true, color: "1a1a1a", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER }
      },
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 36, bold: true, color: "2d5016", font: "Arial" },
        paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 0 }
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 30, bold: true, color: "4a7c23", font: "Arial" },
        paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 }
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 26, bold: true, color: "6b9b37", font: "Arial" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 }
      },
      {
        id: "CodeBlock",
        name: "Code Block",
        basedOn: "Normal",
        run: { font: "Consolas", size: 22, color: "333333" },
        paragraph: { spacing: { before: 100, after: 100 }, indent: { left: 360 } }
      },
      {
        id: "InfoBox",
        name: "Info Box",
        basedOn: "Normal",
        run: { size: 22, color: "444444", italics: true },
        paragraph: { spacing: { before: 120, after: 120 }, indent: { left: 360, right: 360 } }
      }
    ]
  },
  numbering: {
    config: [
      {
        reference: "bullet-list",
        levels: [{
          level: 0,
          format: LevelFormat.BULLET,
          text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbered-list",
        levels: [{
          level: 0,
          format: LevelFormat.DECIMAL,
          text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
        size: { orientation: PageOrientation.PORTRAIT }
      }
    },
    children: [
      // 标题
      new Paragraph({
        heading: HeadingLevel.TITLE,
        children: [new TextRun("BOSS 直聘岗位搜索工作流程")]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "生成时间：2026-03-07 22:20", italics: true, size: 20, color: "666666" }),
          new TextRun({ text: " | ", size: 20 }),
          new TextRun({ text: "搜索城市：深圳", italics: true, size: 20, color: "666666" })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ==================== 第一部分：搜索目标 ====================
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("一、搜索目标与配置")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.1 搜索关键词")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("品牌策划")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("品牌宣传")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("视觉设计")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("品牌设计")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.2 筛选条件")]
      }),

      // 筛选条件表格
      new Table({
        columnWidths: [3120, 3120, 3120],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "条件类型", bold: true, size: 22, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "要求", bold: true, size: 22, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "权重", bold: true, size: 22, color: "FFFFFF" })]
                })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("薪资")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("≥8K，最优 10-15K")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "25%", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("经验")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("1-5 年（可灵活）")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "20%", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("学历")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("大专及以上")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "15%", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("区域")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("排除宝安区")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "15%", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("行业")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("电商/广告/文化传媒")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "15%", bold: true })] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("技能")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun("品牌策划/新媒体/PPT")] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 3120, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "10%", bold: true })] })]
              })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ==================== 第二部分：工作流程 ====================
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("二、搜索工作流程")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("2.1 整体流程图")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "清理浏览器缓存和 Cookie", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("目的：避免旧数据干扰，获取最新搜索结果")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "构建搜索 URL", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("格式：https://www.zhipin.com/web/geek/job?city=101280600&query=关键词")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "打开浏览器并导航", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("使用 browser.open() 打开新标签页")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "等待页面完全加载", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("关键步骤！BOSS 直聘加载较慢，需等待 15-20 秒")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "获取职位列表快照", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("使用 browser.snapshot() 获取页面结构")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "提取职位信息", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("解析 aria-ref 选择器，提取职位标题、薪资、公司、区域等")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "过滤排除区域", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("移除宝安区等不符合要求的职位")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "进入职位详情页", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("逐个访问职位 URL，获取完整职位描述、福利、要求等")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "计算匹配度分数", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("根据权重算法计算每个职位的匹配度（0-100%）")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "筛选并排序", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("保留匹配度≥75% 的职位，按分数降序排列")]
      }),

      new Paragraph({
        numbering: { reference: "numbered-list", level: 0 },
        children: [new TextRun({ text: "去重处理", bold: true })]
      }),
      new Paragraph({
        children: [new TextRun("30 天内已查看的职位不再重复推荐")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ==================== 第三部分：匹配算法 ====================
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("三、匹配度计算算法")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.1 算法公式")]
      }),

      new Paragraph({
        style: "InfoBox",
        children: [
          new TextRun({ text: "匹配度 = ", bold: true }),
          new TextRun("Σ(单项得分 × 权重)"),
          new TextRun({ text: "\n\n阈值：≥75% 视为高匹配职位", italics: true })
        ]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.2 详细计算逻辑")]
      }),

      // 算法表格
      new Table({
        columnWidths: [2340, 4680, 2340],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "维度", bold: true, size: 22, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "计算规则", bold: true, size: 22, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "权重", bold: true, size: 22, color: "FFFFFF" })]
                })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun({ text: "薪资匹配", bold: true })] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("薪资≥8K：得满分")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("薪资 6.4K-8K：得 50% 分")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("薪资<6.4K：不得分")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("25%") ] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun({ text: "经验匹配", bold: true })] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("岗位要求经验范围与 1-5 年有交集：得满分")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("经验不限：得满分")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("要求 5-10 年但其他条件优秀：酌情给分")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("20%") ] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun({ text: "学历匹配", bold: true })] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("大专及以上：得满分")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("不限：得满分")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("15%") ] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun({ text: "区域匹配", bold: true })] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("非宝安区：得满分")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("宝安区：直接排除")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("15%") ] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun({ text: "行业匹配", bold: true })] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("电子商务/广告营销/文化传媒/互联网：得满分")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("其他行业：不得分")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("15%") ] })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ children: [new TextRun({ text: "技能匹配", bold: true })] })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("匹配技能数/总技能数 × 权重")]
                  }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("核心技能：品牌策划、新媒体、文案撰写、PPT")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("10%") ] })]
              })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ==================== 第四部分：技术实现 ====================
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("四、技术实现细节")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.1 浏览器操作流程")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.1.1 清理缓存")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "await browser.clearCookies('zhipin.com');\n", font: "Consolas" }),
          new TextRun({ text: "await browser.clearCache();", font: "Consolas" })
        ]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.1.2 打开页面")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "const { targetId } = await browser.open(url);\n", font: "Consolas" }),
          new TextRun({ text: "// 返回目标标签页 ID 用于后续操作", font: "Consolas", italics: true, color: "666666" })
        ]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.1.3 等待页面加载（关键！）")]
      }),
      new Paragraph({
        children: [new TextRun("BOSS 直聘页面加载较慢，需要等待足够时间确保数据完全加载：")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "async function waitForPageLoad(timeout = 20000) {\n", font: "Consolas" }),
          new TextRun({ text: "  let snapshot;\n", font: "Consolas" }),
          new TextRun({ text: "  const startTime = Date.now();\n", font: "Consolas" }),
          new TextRun({ text: "  \n", font: "Consolas" }),
          new TextRun({ text: "  while (Date.now() - startTime < timeout) {\n", font: "Consolas" }),
          new TextRun({ text: "    snapshot = await browser.snapshot({ refs: 'aria' });\n", font: "Consolas" }),
          new TextRun({ text: "    \n", font: "Consolas" }),
          new TextRun({ text: "    // 检查是否还在加载\n", font: "Consolas" }),
          new TextRun({ text: "    if (!snapshot.text?.includes('正在加载中')) {\n", font: "Consolas" }),
          new TextRun({ text: "      break;\n", font: "Consolas" }),
          new TextRun({ text: "    }\n", font: "Consolas" }),
          new TextRun({ text: "    await sleep(1000);\n", font: "Consolas" }),
          new TextRun({ text: "  }\n", font: "Consolas" }),
          new TextRun({ text: "  return snapshot;\n", font: "Consolas" }),
          new TextRun({ text: "}", font: "Consolas" })
        ]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.1.4 提取职位数据")]
      }),
      new Paragraph({
        children: [new TextRun("使用 aria-ref 选择器解析页面结构：")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "const jobElements = snapshot.querySelectorAll('[ref]');\n", font: "Consolas" }),
          new TextRun({ text: "\n", font: "Consolas" }),
          new TextRun({ text: "for (const el of jobElements) {\n", font: "Consolas" }),
          new TextRun({ text: "  const job = {\n", font: "Consolas" }),
          new TextRun({ text: "    title: el.querySelector('link')?.text,\n", font: "Consolas" }),
          new TextRun({ text: "    salary: el.querySelector('generic')?.text,\n", font: "Consolas" }),
          new TextRun({ text: "    company: el.querySelector('link')?.text,\n", font: "Consolas" }),
          new TextRun({ text: "    district: el.querySelector('generic')?.text,\n", font: "Consolas" }),
          new TextRun({ text: "    url: el.querySelector('link')?.url\n", font: "Consolas" }),
          new TextRun({ text: "  };\n", font: "Consolas" }),
          new TextRun({ text: "}", font: "Consolas" })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.2 错误处理机制")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.2.1 页面加载失败处理")]
      }),
      new Paragraph({
        style: "InfoBox",
        children: [new TextRun("策略：清理缓存 → 重试 → 通知用户手动处理")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "async function handleLoadFailure(error) {\n", font: "Consolas" }),
          new TextRun({ text: "  console.error('页面加载失败:', error);\n", font: "Consolas" }),
          new TextRun({ text: "  await browserWorkflow.clearCache();\n", font: "Consolas" }),
          new TextRun({ text: "  throw new Error('页面加载失败，已清理缓存，请手动重试');\n", font: "Consolas" }),
          new TextRun({ text: "}", font: "Consolas" })
        ]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.2.2 验证码检测")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "async function handleCaptcha(snapshot) {\n", font: "Consolas" }),
          new TextRun({ text: "  if (snapshot.text?.includes('验证码') ||\n", font: "Consolas" }),
          new TextRun({ text: "      snapshot.text?.includes('安全验证')) {\n", font: "Consolas" }),
          new TextRun({ text: "    throw new Error('遇到验证码验证，请手动完成验证后继续');\n", font: "Consolas" }),
          new TextRun({ text: "  }\n", font: "Consolas" }),
          new TextRun({ text: "}", font: "Consolas" })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.3 降低风控风险策略")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.3.1 随机延迟")]
      }),
      new Paragraph({
        children: [new TextRun("在每次点击或翻页间增加 3-8 秒的随机延迟：")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "function randomDelay(min, max) {\n", font: "Consolas" }),
          new TextRun({ text: "  return new Promise(resolve =>\n", font: "Consolas" }),
          new TextRun({ text: "    setTimeout(resolve, Math.random() * (max - min) + min)\n", font: "Consolas" }),
          new TextRun({ text: "  );\n", font: "Consolas" }),
          new TextRun({ text: "}\n", font: "Consolas" }),
          new TextRun({ text: "\n", font: "Consolas" }),
          new TextRun({ text: "// 使用示例\n", font: "Consolas" }),
          new TextRun({ text: "await randomDelay(3000, 8000);", font: "Consolas" })
        ]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun("4.3.2 模拟人类行为")]
      }),
      new Paragraph({
        children: [new TextRun("在点击前执行模拟滚动，伪造人类阅读行为：")]
      }),
      new Paragraph({
        style: "CodeBlock",
        children: [
          new TextRun({ text: "async function simulateHumanBehavior() {\n", font: "Consolas" }),
          new TextRun({ text: "  // 随机滚动\n", font: "Consolas" }),
          new TextRun({ text: "  await browser.evaluate(() => {\n", font: "Consolas" }),
          new TextRun({ text: "    window.scrollBy(0, Math.random() * 300 + 100);\n", font: "Consolas" }),
          new TextRun({ text: "  });\n", font: "Consolas" }),
          new TextRun({ text: "  \n", font: "Consolas" }),
          new TextRun({ text: "  await randomDelay(1000, 3000);\n", font: "Consolas" }),
          new TextRun({ text: "  \n", font: "Consolas" }),
          new TextRun({ text: "  // 再次滚动\n", font: "Consolas" }),
          new TextRun({ text: "  await browser.evaluate(() => {\n", font: "Consolas" }),
          new TextRun({ text: "    window.scrollBy(0, Math.random() * 300 + 100);\n", font: "Consolas" }),
          new TextRun({ text: "  });\n", font: "Consolas" }),
          new TextRun({ text: "}", font: "Consolas" })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ==================== 第五部分：实际案例 ====================
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("五、实际搜索案例")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("5.1 高匹配职位示例")]
      }),

      // 职位案例表格
      new Table({
        columnWidths: [2340, 4680, 2340],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({
            tableHeader: true,
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "职位", bold: true, size: 22, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "详细信息", bold: true, size: 22, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                shading: { fill: "4A7C23", type: ShadingType.CLEAR },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "匹配度", bold: true, size: 22, color: "FFFFFF" })]
                })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun({ text: "品牌策划", bold: true })] }),
                  new Paragraph({ children: [new TextRun({ text: "理想成", size: 20, color: "666666" })] })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun("薪资：11-15K | 经验：3-5 年 | 学历：大专")] }),
                  new Paragraph({ children: [new TextRun("区域：龙华区 | 行业：电子商务/大健康")] }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("亮点：抖音全球购 TOP1、13 天春节假")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "85%", bold: true, color: "4A7C23", size: 28 })]
                })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun({ text: "高级品牌策划", bold: true })] }),
                  new Paragraph({ children: [new TextRun({ text: "深圳美山实业", size: 20, color: "666666" })] })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun("薪资：12-16K | 经验：3-5 年 | 学历：大专")] }),
                  new Paragraph({ children: [new TextRun("区域：龙华区 | 行业：日化/日本商社")] }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("亮点：日本总部、会日语优先")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "75%", bold: true, color: "4A7C23", size: 28 })]
                })]
              })
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun({ text: "品牌策划", bold: true })] }),
                  new Paragraph({ children: [new TextRun({ text: "嘉方传媒", size: 20, color: "666666" })] })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 4680, type: WidthType.DXA },
                children: [
                  new Paragraph({ children: [new TextRun("薪资：15-30K·13 薪 | 经验：1-3 年 | 学历：大专")] }),
                  new Paragraph({ children: [new TextRun("区域：南山区 | 行业：广告营销")] }),
                  new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun("亮点：服务 OPPO/网易/腾讯、B 站原住民")]
                  })
                ]
              }),
              new TableCell({
                borders: cellBorders,
                width: { size: 2340, type: WidthType.DXA },
                children: [new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: "82%", bold: true, color: "4A7C23", size: 28 })]
                })]
              })
            ]
          })
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ==================== 第六部分：总结 ====================
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("六、总结与优化建议")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("6.1 核心要点")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "等待页面完全加载是成功抓取的关键", bold: true })]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "使用 aria-ref 选择器比 class 更稳定", bold: true })]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "随机延迟和模拟人类行为可降低风控风险", bold: true })]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "多维度匹配算法确保推荐质量", bold: true })]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "去重机制避免重复推荐", bold: true })]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("6.2 优化建议")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("增加更多关键词：新媒体运营、内容策划、市场推广")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("扩展搜索城市：广州、杭州、上海")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("添加公司规模筛选：优先 100-499 人成长型公司")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("增加福利权重：五险一金、年终奖、带薪年假")]
      }),
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("记录投递状态：已沟通/已投递/面试中/已 offer")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // ==================== 附录：完整代码 ====================
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("附录：完整代码文件")]
      }),

      new Paragraph({
        children: [
          new TextRun("完整代码已保存至："),
          new TextRun({ text: "boss-search-workflow.js", bold: true, underline: { type: UnderlineType.SINGLE } })
        ]
      }),

      new Paragraph({
        children: [new TextRun("文件位置：C:\\Users\\TR\\.openclaw\\workspace\\")]
      }),

      new Paragraph({
        style: "InfoBox",
        children: [
          new TextRun({ text: "提示：", bold: true }),
          new TextRun("运行代码需要 Node.js 环境和 docx 库。")
        ]
      }),

      // 文档结束
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "— 文档结束 —", italics: true, color: "999999" }),
          new TextRun({ text: "\n生成时间：2026-03-07 22:20", size: 18, color: "999999" })
        ]
      })
    ]
  }]
});

// ==================== 导出文档 ====================
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("BOSS 直聘搜索工作流程.docx", buffer);
  console.log("文档生成成功：BOSS 直聘搜索工作流程.docx");
}).catch(error => {
  console.error("文档生成失败:", error);
});
