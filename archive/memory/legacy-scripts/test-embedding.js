/**
 * 豆包 Embedding API 实际测试脚本
 */

const https = require('https');

const CONFIG = {
  baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
  apiKey: 'fddc1778-d04c-403e-8327-ab68ec1ec9dd',
  model: 'doubao-embedding-vision-251215',
  endpoint: '/embeddings/multimodal'
};

async function testEmbedding() {
  const testText = `OpenClaw 记忆系统测试 - ${Date.now()}`;
  
  const multimodalInput = [{
    type: 'text',
    text: testText
  }];
  
  const requestBody = {
    model: CONFIG.model,
    input: multimodalInput,
    encoding_format: 'float'
  };
  
  const data = JSON.stringify(requestBody);
  
  console.log('📤 发送请求...');
  console.log('文本:', testText);
  console.log('模型:', CONFIG.model);
  console.log('端点:', `https://ark.cn-beijing.volces.com/api/v3${CONFIG.endpoint}`);
  console.log('');
  
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const options = {
      hostname: 'ark.cn-beijing.volces.com',
      path: `/api/v3${CONFIG.endpoint}`,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CONFIG.apiKey}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };
    
    const req = https.request(options, (res) => {
      let responseBody = '';
      
      console.log('📥 响应状态:', res.statusCode);
      console.log('响应头:', JSON.stringify(res.headers, null, 2));
      console.log('');
      
      res.on('data', (chunk) => {
        responseBody += chunk;
      });
      
      res.on('end', () => {
        const duration = Date.now() - startTime;
        console.log('⏱️ 耗时:', duration, 'ms');
        console.log('');
        
        try {
          const response = JSON.parse(responseBody);
          
          if (res.statusCode === 200 && response.data && response.data.embedding) {
            console.log('✅ 调用成功！');
            console.log('');
            console.log('响应详情:');
            console.log('  - Request ID:', response.id);
            console.log('  - Model:', response.model);
            console.log('  - 向量维度:', response.data.embedding.length);
            console.log('  - Prompt Tokens:', response.usage?.prompt_tokens || 'N/A');
            console.log('  - Total Tokens:', response.usage?.total_tokens || 'N/A');
            console.log('  - Created:', new Date(response.created * 1000).toLocaleString('zh-CN'));
            console.log('');
            console.log('向量前 10 个值:', response.data.embedding.slice(0, 10));
            
            resolve({
              success: true,
              requestId: response.id,
              model: response.model,
              dimensions: response.data.embedding.length,
              tokens: response.usage,
              vector: response.data.embedding
            });
          } else {
            console.log('❌ API 返回错误:');
            console.log(JSON.stringify(response, null, 2));
            reject(new Error(`API error: ${JSON.stringify(response)}`));
          }
        } catch (e) {
          console.log('❌ 解析响应失败:');
          console.log(responseBody.substring(0, 500));
          reject(new Error(`Parse error: ${e.message}`));
        }
      });
    });
    
    req.on('error', (e) => {
      console.log('❌ 请求错误:', e.message);
      reject(new Error(`Request error: ${e.message}`));
    });
    
    console.log('');
    req.write(data);
    req.end();
  });
}

// 运行测试
testEmbedding()
  .then(result => {
    console.log('');
    console.log('='.repeat(50));
    console.log('🎉 测试完成！');
    console.log('='.repeat(50));
    process.exit(0);
  })
  .catch(err => {
    console.log('');
    console.log('='.repeat(50));
    console.log('💥 测试失败！');
    console.log('='.repeat(50));
    console.error('错误:', err.message);
    process.exit(1);
  });
