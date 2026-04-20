const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, TableOfContents,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, ExternalHyperlink,
        HeadingLevel, BorderStyle, WidthType, UnderlineType, ShadingType, VerticalAlign,
        PageBreak } = require('docx');
const fs = require('fs');

// ==================== 配置参数 ====================
const CONFIG = {
  keywords: ['品牌策划', '品牌宣传', '视觉设计', '品牌设计'],
  city: '深圳',
  cityCode: '101280600',
  excludeDistricts: ['宝安区'],
  salaryMin: 8000,
  salaryOptimal: { min: 10000, max: 15000 },
  experience: { min: 1, max: 5 }, // 年
  matchThreshold: 0.75, // 75% 匹配度
  dedupDays: 30,
};

// ==================== 匹配度计算逻辑 ====================
function calculateMatchScore(job, requirements) {
  let score = 0;
  let weights = {
    salary: 0.25,
    experience: 0.20,
    education: 0.15,
    location: 0.15,
    industry: 0.15,
    skills: 0.10
  };

  // 薪资匹配 (25%)
  const jobSalaryMin = parseSalary(job.salaryMin);
  if (jobSalaryMin >= requirements.salaryMin) {
    score += weights.salary;
  } else if (jobSalaryMin >= requirements.salaryMin * 0.8) {
    score += weights.salary * 0.5;
  }

  // 经验匹配 (20%)
  const jobExpMin = parseExperience(job.experienceMin);
  const jobExpMax = parseExperience(job.experienceMax);
  if (jobExpMin <= requirements.experience.max && jobExpMax >= requirements.experience.min) {
    score += weights.experience;
  }

  // 学历匹配 (15%)
  const educationRank = { '大专': 1, '本科': 2, '硕士': 3, '博士': 4 };
  if (educationRank[job.education] >= educationRank[requirements.education]) {
    score += weights.education;
  }

  // 区域匹配 (15%)
  if (!requirements.excludeDistricts.includes(job.district)) {
    score += weights.location;
  }

  // 行业匹配 (15%)
  const preferredIndustries = ['电子商务', '广告营销', '文化传媒', '互联网'];
  if (preferredIndustries.includes(job.industry)) {
    score += weights.industry;
  }

  // 技能匹配 (10%)
  const requiredSkills = ['品牌策划', '新媒体', '文案撰写', 'PPT'];
  const matchSkills = job.skills.filter(s => requiredSkills.includes(s));
  score += weights.skills * (matchSkills.length / requiredSkills.length);

  return score;
}

// ==================== BOSS 直聘搜索流程 ====================
async function searchBossZhipin() {
  const results = [];

  for (const keyword of CONFIG.keywords) {
    // 步骤 1: 构建搜索 URL
    const searchUrl = buildSearchUrl(keyword, CONFIG.cityCode);

    // 步骤 2: 打开浏览器并导航
    await browser.navigate(searchUrl);

    // 步骤 3: 等待页面加载 (关键！BOSS 直聘加载慢)
    await waitForPageLoad(15000);

    // 步骤 4: 获取职位列表
    const jobList = await extractJobList();

    // 步骤 5: 过滤排除区域
    const filteredJobs = jobList.filter(job =>
      !CONFIG.excludeDistricts.includes(job.district)
    );

    // 步骤 6: 进入详情页获取完整信息
    for (const job of filteredJobs) {
      const detail = await getJobDetail(job.url);

      // 步骤 7: 计算匹配度
      const matchScore = calculateMatchScore(detail, CONFIG);

      // 步骤 8: 筛选匹配度≥75% 的职位
      if (matchScore >= CONFIG.matchThreshold) {
        results.push({
          ...detail,
          matchScore,
          keyword,
          searchedAt: new Date().toISOString()
        });
      }

      // 步骤 9: 随机延迟 (避免风控)
      await randomDelay(3000, 8000);
    }
  }

  return results;
}

// ==================== 浏览器操作流程 ====================
const browserWorkflow = {
  // 1. 清理缓存和 Cookie
  clearCache: async () => {
    await browser.clearCookies('zhipin.com');
    await browser.clearCache();
  },

  // 2. 打开新标签页
  openTab: async (url) => {
    const { targetId } = await browser.open(url);
    return targetId;
  },

  // 3. 等待页面稳定 (关键步骤)
  waitForStable: async (timeout = 20000) => {
    let snapshot;
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      snapshot = await browser.snapshot({ refs: 'aria', timeoutMs: 5000 });

      // 检查是否还在加载
      if (!snapshot.text?.includes('正在加载中') &&
          !snapshot.text?.includes('BOSS 正在加载中')) {
        break;
      }

      await sleep(1000);
    }

    return snapshot;
  },

  // 4. 使用稳定选择器提取数据
  extractJobList: async (snapshot) => {
    const jobs = [];

    // 使用 aria-ref 或文本选择器 (更稳定)
    const jobElements = snapshot.querySelectorAll('[ref]');

    for (const el of jobElements) {
      const job = {
        title: el.querySelector('link')?.text,
        salary: el.querySelector('generic')?.text,
        company: el.querySelector('link')?.text,
        district: el.querySelector('generic')?.text,
        experience: el.querySelector('listitem')?.text,
        education: el.querySelector('listitem')?.text,
        url: el.querySelector('link')?.url
      };

      if (job.title && job.url) {
        jobs.push(job);
      }
    }

    return jobs;
  },

  // 5. 模拟人类行为 (降低风控风险)
  simulateHumanBehavior: async () => {
    // 随机滚动
    await browser.evaluate(() => {
      window.scrollBy(0, Math.random() * 300 + 100);
    });

    await randomDelay(1000, 3000);

    // 再次滚动
    await browser.evaluate(() => {
      window.scrollBy(0, Math.random() * 300 + 100);
    });

    await randomDelay(1000, 2000);
  }
};

// ==================== 错误处理机制 ====================
const errorHandler = {
  // 页面加载失败
  handleLoadFailure: async (error) => {
    console.error('页面加载失败:', error);
    await browserWorkflow.clearCache();
    throw new Error('页面加载失败，已清理缓存，请手动重试');
  },

  // 遇到验证码
  handleCaptcha: async (snapshot) => {
    if (snapshot.text?.includes('验证码') ||
        snapshot.text?.includes('安全验证')) {
      throw new Error('遇到验证码验证，请手动完成验证后继续');
    }
  },

  // 选择器失败重试
  retryWithFallback: async (operation, maxRetries = 3) => {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await operation();
      } catch (error) {
        if (i === maxRetries - 1) throw error;
        await randomDelay(2000 * (i + 1), 4000 * (i + 1));
      }
    }
  }
};

// ==================== 辅助函数 ====================
function buildSearchUrl(keyword, cityCode) {
  const encodedKeyword = encodeURIComponent(keyword);
  return `https://www.zhipin.com/web/geek/job?city=${cityCode}&query=${encodedKeyword}`;
}

function parseSalary(salaryStr) {
  // 解析 "10-15K" 为数字
  const match = salaryStr.match(/(\d+)-?(\d*)?[Kk]/);
  if (match) {
    return parseInt(match[1]) * 1000;
  }
  return 0;
}

function parseExperience(expStr) {
  const expMap = {
    '经验不限': 0,
    '1 年以内': 0,
    '1-3 年': 1,
    '3-5 年': 3,
    '5-10 年': 5,
    '10 年以上': 10
  };
  return expMap[expStr] || 0;
}

function randomDelay(min, max) {
  return new Promise(resolve =>
    setTimeout(resolve, Math.random() * (max - min) + min)
  );
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ==================== 主执行流程 ====================
async function main() {
  console.log('开始 BOSS 直聘搜索任务...');

  try {
    // 1. 清理缓存
    await browserWorkflow.clearCache();

    // 2. 执行搜索
    const results = await searchBossZhipin();

    // 3. 去重
    const dedupedResults = deduplicate(results, CONFIG.dedupDays);

    // 4. 按匹配度排序
    dedupedResults.sort((a, b) => b.matchScore - a.matchScore);

    // 5. 输出结果
    console.log(`找到 ${dedupedResults.length} 个匹配职位`);

    return dedupedResults;

  } catch (error) {
    console.error('搜索失败:', error.message);
    throw error;
  }
}

// 运行
main();
