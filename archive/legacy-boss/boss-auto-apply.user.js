// ==UserScript==
// @name         BOSS 直聘自动投递 - 王庆专用 v4
// @namespace    http://tampermonkey.net/
// @version      4.0
// @description  根据匹配逻辑自动筛选并投递品牌策划岗位 - 当前页直接操作版
// @author       青 (AI Assistant)
// @match        https://www.zhipin.com/web/geek/job*
// @match        https://www.zhipin.com/web/geek/jobs*
// @match        https://www.zhipin.com/job_detail/*.html
// @grant        GM_setValue
// @grant        GM_getValue
// @grant        GM_notification
// @run-at       document-end
// ==/UserScript==

(function() {
    'use strict';

    // ==================== 配置区 ====================
    const CONFIG = {
        keywords: ['品牌策划', '品牌宣传', '视觉设计', '品牌设计', '品牌视觉'],
        excludeLocations: ['宝安'],
        minSalary: 8,
        maxSalary: 15,
        minExperience: 1,
        maxExperience: 5,
        education: ['大专', '本科', '学历不限', '高中', '中专', '中技'],
        targetIndustries: ['广告', '策划', '品牌咨询', '营销服务', '快消', '文旅', '互联网', '科技', '文化传播', '传媒'],
        delayBetweenJobs: 8000,
        delayAfterApply: 3000,
        maxApplications: 30,
        autoApply: true,
        defaultGreeting: '您好，我对这个职位很感兴趣。我有 3 年 + 品牌策划经验，擅长品牌从 0-1 建设、大型活动策划和全渠道传播。希望能有机会进一步沟通！'
    };

    // ==================== 状态管理 ====================
    let state = {
        appliedCount: 0,
        scannedCount: 0,
        matchedCount: 0,
        rejectedCount: 0,
        isRunning: false,
        currentJobUrl: null,
        processedJobs: new Set()
    };

    // ==================== 工具函数 ====================
    function log(message, type = 'info') {
        const prefix = '[BOSS 自动投递]';
        const timestamp = new Date().toLocaleTimeString();
        console.log(`${prefix} [${timestamp}] ${message}`);

        const logBox = document.getElementById('boss-auto-apply-log') || createLogBox();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.style.cssText = 'padding: 3px 0; border-bottom: 1px solid #333; font-size: 11px;';

        const colors = {
            'info': '#0f0',
            'success': '#0f0',
            'warn': '#ffa500',
            'error': '#f00'
        };
        logEntry.style.color = colors[type] || '#0f0';
        logEntry.textContent = `[${timestamp}] ${message}`;
        logBox.appendChild(logEntry);
        logBox.scrollTop = logBox.scrollHeight;
    }

    function createLogBox() {
        const logBox = document.createElement('div');
        logBox.id = 'boss-auto-apply-log';
        logBox.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 450px;
            max-height: 500px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.95);
            color: #0f0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
            padding: 15px;
            border-radius: 8px;
            z-index: 9999999;
            box-shadow: 0 4px 30px rgba(0,0,0,0.5);
            border: 1px solid #333;
        `;
        document.body.appendChild(logBox);
        return logBox;
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function parseSalary(salaryText) {
        if (!salaryText) return { min: 0, max: 0 };
        const match = salaryText.match(/(\d+)-(\d+)K/);
        if (match) {
            return { min: parseInt(match[1]), max: parseInt(match[2]) };
        }
        return { min: 0, max: 0 };
    }

    function parseExperience(expText) {
        if (!expText) return { min: 0, max: 99 };
        if (expText.includes('以内') || expText.includes('应届') || expText.includes('毕业生')) return { min: 0, max: 1 };
        if (expText.includes('年以上')) {
            const match = expText.match(/(\d+)年以上/);
            return { min: parseInt(match[1]) || 0, max: 99 };
        }
        const match = expText.match(/(\d+)-(\d+)年/);
        if (match) {
            return { min: parseInt(match[1]), max: parseInt(match[2]) };
        }
        return { min: 0, max: 99 };
    }

    // ==================== 匹配逻辑 ====================
    function checkLocation(location) {
        for (const exclude of CONFIG.excludeLocations) {
            if (location && location.includes(exclude)) {
                return false;
            }
        }
        return true;
    }

    function checkSalary(salaryText) {
        const salary = parseSalary(salaryText);
        if (salary.min === 0) return true;
        return salary.max >= CONFIG.minSalary && salary.min <= CONFIG.maxSalary;
    }

    function checkEducation(eduText) {
        if (!eduText || eduText.includes('不限') || eduText.includes('以上')) return true;
        return CONFIG.education.some(edu => eduText.includes(edu));
    }

    function checkExperience(expText) {
        const exp = parseExperience(expText);
        return exp.min <= CONFIG.maxExperience && exp.max >= CONFIG.minExperience;
    }

    function calculateMatchScore(jobInfo) {
        let score = 0;
        let maxScore = 0;

        maxScore += 30;
        const salary = parseSalary(jobInfo.salary);
        if (salary.min >= CONFIG.minSalary && salary.max <= CONFIG.maxSalary) {
            score += 30;
        } else if (salary.max >= CONFIG.minSalary && salary.min <= CONFIG.maxSalary) {
            score += 20;
        } else if (salary.max >= CONFIG.minSalary) {
            score += 10;
        }

        maxScore += 25;
        const exp = parseExperience(jobInfo.experience);
        if (exp.min <= 3 && exp.max >= 3) {
            score += 25;
        } else if (exp.min <= 5 && exp.max >= 2) {
            score += 15;
        } else if (exp.min <= 5) {
            score += 5;
        }

        maxScore += 20;
        if (checkEducation(jobInfo.education)) {
            score += 20;
        }

        maxScore += 15;
        if (checkLocation(jobInfo.location)) {
            score += 15;
        }

        maxScore += 10;
        if (jobInfo.industry && CONFIG.targetIndustries.some(ind => jobInfo.industry.includes(ind))) {
            score += 10;
        }

        return Math.round((score / maxScore) * 100);
    }

    // ==================== 创建控制面板 ====================
    function createControlPanel() {
        if (document.getElementById('boss-auto-apply-panel')) {
            return;
        }

        const panel = document.createElement('div');
        panel.id = 'boss-auto-apply-panel';
        panel.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.95);
            color: #fff;
            padding: 20px;
            border-radius: 12px;
            z-index: 9999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 4px 30px rgba(0,0,0,0.5);
            border: 2px solid #0f0;
            min-width: 220px;
        `;

        panel.innerHTML = `
            <h3 style="margin: 0 0 15px 0; color: #0f0; font-size: 16px;">🤖 BOSS 自动投递 v4.0</h3>
            <div style="font-size: 13px; line-height: 2;">
                <div><span style="color: #888;">扫描:</span> <span id="boss-scanned" style="color: #fff; font-weight: bold;">0</span></div>
                <div><span style="color: #888;">匹配:</span> <span id="boss-matched" style="color: #ffa500; font-weight: bold;">0</span></div>
                <div><span style="color: #888;">投递:</span> <span id="boss-applied" style="color: #0f0; font-weight: bold;">0</span></div>
                <div><span style="color: #888;">排除:</span> <span id="boss-rejected" style="color: #f00; font-weight: bold;">0</span></div>
            </div>
            <div style="margin-top: 15px; display: flex; gap: 10px;">
                <button id="boss-start-btn" style="
                    background: linear-gradient(135deg, #0f0, #00cc00);
                    color: #000;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 14px;
                    flex: 1;
                    transition: all 0.3s;
                ">▶ 开始</button>
                <button id="boss-stop-btn" style="
                    background: linear-gradient(135deg, #f00, #cc0000);
                    color: #fff;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: bold;
                    font-size: 14px;
                    flex: 1;
                    transition: all 0.3s;
                ">⏹ 停止</button>
            </div>
            <div style="margin-top: 10px; font-size: 11px; color: #888; text-align: center;">
                🎯 ${CONFIG.minSalary}-${CONFIG.maxSalary}K | 排除宝安 | ≥70% 匹配
            </div>
            <div style="margin-top: 5px; font-size: 10px; color: #666; text-align: center;">
                ℹ️ 当前页直接操作，无需新标签页
            </div>
        `;

        document.body.appendChild(panel);

        document.getElementById('boss-start-btn').addEventListener('click', () => {
            if (state.isRunning) {
                log('⚠️ 任务已在运行中', 'warn');
                return;
            }
            log('✅ 开始执行自动投递...', 'success');
            processJobList();
        });

        document.getElementById('boss-stop-btn').addEventListener('click', () => {
            state.isRunning = false;
            log('⏹️ 任务已停止', 'warn');
        });

        log('🎉 控制面板已创建', 'success');
    }

    function updatePanel() {
        const scanned = document.getElementById('boss-scanned');
        const matched = document.getElementById('boss-matched');
        const applied = document.getElementById('boss-applied');
        const rejected = document.getElementById('boss-rejected');

        if (scanned) scanned.textContent = state.scannedCount;
        if (matched) matched.textContent = state.matchedCount;
        if (applied) applied.textContent = state.appliedCount;
        if (rejected) rejected.textContent = state.rejectedCount;
    }

    // ==================== 列表页处理 ====================
    async function processJobList() {
        log('=== 🚀 开始处理职位列表 ===', 'success');
        state.isRunning = true;

        const selectors = [
            '[class*="job-card"]',
            '[class*="job-card_"]',
            '.job-card',
            '[data-ved]',
            'li[class*="column"]',
            '[class*="recommend-job"]',
            '[geek="job-card"]'
        ];

        let jobCards = [];
        for (const selector of selectors) {
            jobCards = document.querySelectorAll(selector);
            if (jobCards.length > 0) {
                log(`📍 找到选择器 "${selector}" 匹配 ${jobCards.length} 个职位`, 'success');
                break;
            }
        }

        if (jobCards.length === 0) {
            log('⚠️ 未找到职位卡片，尝试查找所有列表项...', 'warn');
            jobCards = document.querySelectorAll('li');
        }

        log(`📊 共找到 ${jobCards.length} 个职位`, 'info');

        for (let i = 0; i < jobCards.length && state.isRunning && state.appliedCount < CONFIG.maxApplications; i++) {
            const card = jobCards[i];

            const jobId = card.getAttribute('data-job-id') || card.innerText.substring(0, 50);
            if (state.processedJobs.has(jobId)) {
                continue;
            }
            state.processedJobs.add(jobId);

            state.scannedCount++;
            updatePanel();

            const jobInfo = extractJobInfoFromCard(card);
            log(`[${state.scannedCount}] ${jobInfo.title} | ${jobInfo.salary} | ${jobInfo.location} | ${jobInfo.experience} | ${jobInfo.education}`);

            let rejectReason = null;

            if (!checkLocation(jobInfo.location)) {
                rejectReason = `地点不符 (${jobInfo.location})`;
            } else if (!checkSalary(jobInfo.salary)) {
                rejectReason = `薪资不符 (${jobInfo.salary})`;
            } else if (!checkEducation(jobInfo.education)) {
                rejectReason = `学历不符 (${jobInfo.education})`;
            } else if (!checkExperience(jobInfo.experience)) {
                rejectReason = `经验不符 (${jobInfo.experience})`;
            }

            if (rejectReason) {
                state.rejectedCount++;
                updatePanel();
                log(`❌ 排除：${rejectReason}`, 'error');
                markCard(card, 'rejected', rejectReason);
                continue;
            }

            const matchScore = calculateMatchScore(jobInfo);
            log(`📈 匹配度：${matchScore}%`, matchScore >= 70 ? 'success' : 'warn');

            if (matchScore >= 70) {
                state.matchedCount++;
                updatePanel();
                markCard(card, 'matched', `${matchScore}%`);

                const jobLink = card.querySelector('a[href*="/job_detail/"]');
                if (jobLink) {
                    log(`🎯 准备投递：${jobInfo.title}`, 'success');
                    await applyForJob(jobLink.href, card);
                } else {
                    log('⚠️ 未找到职位链接', 'warn');
                }
            } else {
                state.rejectedCount++;
                updatePanel();
                markCard(card, 'low-match', `${matchScore}%`);
            }

            await sleep(CONFIG.delayBetweenJobs);
        }

        state.isRunning = false;
        log('=== ✅ 列表页处理完成 ===', 'success');
        showSummary();
    }

    function extractJobInfoFromCard(card) {
        const text = card.innerText;
        const lines = text.split('\n').map(l => l.trim()).filter(l => l);

        return {
            title: lines[0] || '',
            salary: lines[1] || '',
            location: lines[lines.length - 1] || '',
            experience: lines[2] || '',
            education: lines[3] || '',
            company: lines[lines.length - 2] || '',
            industry: ''
        };
    }

    function markCard(card, status, reason) {
        const colors = {
            'matched': '#00ff00',
            'rejected': '#ff0000',
            'low-match': '#ffa500',
            'applying': '#00ffff'
        };

        card.style.border = `3px solid ${colors[status] || '#fff'}`;
        card.style.position = 'relative';
        card.style.zIndex = '10';

        const oldBadge = card.querySelector('.boss-auto-apply-badge');
        if (oldBadge) oldBadge.remove();

        const badge = document.createElement('div');
        badge.className = 'boss-auto-apply-badge';
        badge.textContent = reason;
        badge.style.cssText = `
            position: absolute;
            top: 5px;
            right: 5px;
            background: ${colors[status]};
            color: #000;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        `;
        card.appendChild(badge);
    }

    // ==================== 投递逻辑（当前页直接操作）====================
    async function applyForJob(jobUrl, card) {
        try {
            log(`📤 正在处理：${jobUrl}`, 'info');
            markCard(card, 'applying', '投递中...');

            // 记录当前 URL 以便返回
            const originalUrl = window.location.href;

            // 直接在当前页面导航到职位详情
            window.location.href = jobUrl;

            // 等待页面加载
            await sleep(5000);

            // 等待并查找"立即沟通"按钮
            let applyButton = null;
            const buttonSelectors = [
                '[class*="apply-btn"]',
                '[class*="chat-btn"]',
                '[class*="communicate-btn"]',
                'button[class*="apply"]',
                'button[class*="chat"]',
                'a[class*="apply"]',
                'a[class*="chat"]',
                '[data-click="apply"]',
                '[data-click="chat"]'
            ];

            for (let attempt = 0; attempt < 5 && !applyButton; attempt++) {
                for (const selector of buttonSelectors) {
                    const buttons = document.querySelectorAll(selector);
                    for (const btn of buttons) {
                        const text = btn.innerText || btn.textContent || '';
                        if (text.includes('立即沟通') || text.includes('马上沟通') || text.includes('打招呼') || text.includes('立即招呼')) {
                            applyButton = btn;
                            break;
                        }
                    }
                }
                if (!applyButton) {
                    log(`⏳ 第${attempt + 1}次查找按钮...`, 'info');
                    await sleep(2000);
                }
            }

            if (applyButton) {
                log('🖱️ 找到"立即沟通"按钮，正在点击...', 'success');
                applyButton.scrollIntoView({ behavior: 'smooth', block: 'center' });
                await sleep(500);
                applyButton.click();
                log('✅ 已点击"立即沟通"按钮', 'success');

                // 等待聊天窗口打开
                await sleep(3000);

                // 查找输入框并填充问候语
                const inputSelectors = [
                    'textarea[class*="chat"]',
                    'textarea[class*="input"]',
                    'textarea[placeholder*="输入"]',
                    '[contenteditable="true"]'
                ];

                let inputBox = null;
                for (const selector of inputSelectors) {
                    inputBox = document.querySelector(selector);
                    if (inputBox) break;
                }

                if (inputBox) {
                    log('📝 正在填充问候语...', 'info');
                    inputBox.value = CONFIG.defaultGreeting;
                    inputBox.dispatchEvent(new Event('input', { bubbles: true }));
                    inputBox.dispatchEvent(new Event('change', { bubbles: true }));
                    await sleep(1000);

                    // 查找发送按钮
                    const sendSelectors = [
                        'button[class*="send"]',
                        'button[class*="submit"]',
                        '[class*="send-btn"]',
                        '[type="submit"]'
                    ];

                    let sendButton = null;
                    for (const selector of sendSelectors) {
                        const buttons = document.querySelectorAll(selector);
                        for (const btn of buttons) {
                            const text = btn.innerText || btn.textContent || '';
                            if (text.includes('发送') || text.includes('发送') || btn.className.includes('send')) {
                                sendButton = btn;
                                break;
                            }
                        }
                    }

                    if (sendButton) {
                        log('📤 正在发送消息...', 'success');
                        sendButton.click();
                        await sleep(2000);
                        log('✅ 消息已发送', 'success');
                    } else {
                        log('⚠️ 未找到发送按钮，尝试直接按 Enter', 'warn');
                        inputBox.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                    }
                } else {
                    log('⚠️ 未找到输入框', 'warn');
                }

                // 等待片刻后返回列表页
                await sleep(CONFIG.delayAfterApply);
                log('🔙 正在返回列表页...', 'info');

                // 返回原列表页
                window.history.back();
                await sleep(3000);

            } else {
                log('⚠️ 未找到"立即沟通"按钮', 'warn');
                markCard(card, 'error', '无按钮');

                // 直接返回
                await sleep(2000);
                window.history.back();
                await sleep(2000);
            }

            // 记录已投递
            state.appliedCount++;
            updatePanel();
            log(`✅ 投递完成！已投递 ${state.appliedCount}/${CONFIG.maxApplications} 个职位`, 'success');

        } catch (error) {
            log(`❌ 投递失败：${error.message}`, 'error');
            markCard(card, 'error', '投递失败');

            // 尝试返回
            try {
                window.history.back();
            } catch (e) {}
        }
    }

    function showSummary() {
        GM_notification({
            title: '🤖 BOSS 自动投递完成',
            text: `扫描：${state.scannedCount} | 匹配：${state.matchedCount} | 投递：${state.appliedCount} | 排除：${state.rejectedCount}`,
            timeout: 10000
        });
    }

    // ==================== 初始化 ====================
    function init() {
        log('🎉 BOSS 自动投递脚本 v4.0 已加载', 'success');

        const isJobList = window.location.href.includes('/web/geek/job') || window.location.href.includes('/web/geek/jobs');
        const isJobDetail = window.location.href.includes('/job_detail/');

        if (isJobList) {
            log('📋 检测到列表页', 'success');
            createControlPanel();
            setInterval(updatePanel, 1000);
        } else if (isJobDetail) {
            log('📄 检测到详情页', 'success');
            log('ℹ️ 详情页模式：等待自动操作或手动操作', 'info');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
