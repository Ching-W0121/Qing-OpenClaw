# 椋炰功鏈哄櫒浜洪厤缃畬鎴愭姤鍛?
**鏃堕棿**: 2026-03-11 16:50  
**鐘舵€?*: 鉁?閰嶇疆瀹屾垚锛屽緟濉叆鍑瘉

---

## 馃摝 宸插垱寤烘枃浠?
```
integrations/feishu/
鈹溾攢鈹€ feishu_bot.py          # 涓荤▼搴忥紙闀胯繛鎺ュ鎴风锛?鈹溾攢鈹€ .env                   # 閰嶇疆鏂囦欢锛堥渶濉叆鍑瘉锛?鈹溾攢鈹€ .env.example           # 閰嶇疆绀轰緥
鈹溾攢鈹€ .gitignore             # Git 蹇界暐瑙勫垯
鈹溾攢鈹€ check_config.py        # 閰嶇疆妫€鏌ュ伐鍏?鈹溾攢鈹€ start.bat              # 蹇€熷惎鍔ㄨ剼鏈?鈹溾攢鈹€ requirements.txt       # Python 渚濊禆
鈹溾攢鈹€ README.md              # 瀹屾暣浣跨敤鏂囨。
鈹斺攢鈹€ QUICKSTART.md          # 5 鍒嗛挓蹇€熷紑濮嬫寚鍗?```

---

## 鉁?宸插畬鎴愭楠?
### 1. SDK 瀹夎
- 鉁?lark-oapi 1.5.3 宸插畨瑁?- 鉁?python-dotenv 宸插畨瑁?
### 2. 椤圭洰缁撴瀯
- 鉁?鍒涘缓 integrations/feishu/ 鐩綍
- 鉁?鍒涘缓涓荤▼搴?feishu_bot.py
- 鉁?鍒涘缓閰嶇疆鏂囦欢 .env
- 鉁?鍒涘缓妫€鏌ュ伐鍏?check_config.py
- 鉁?鍒涘缓鍚姩鑴氭湰 start.bat

### 3. 鍔熻兘瀹炵幇
- 鉁?闀胯繛鎺?WebSocket 瀹㈡埛绔?- 鉁?浜嬩欢澶勭悊鍣紙v2.0 鍜?v1.0锛?- 鉁?鎺ユ敹娑堟伅浜嬩欢鐩戝惉
- 鉁?鐜鍙橀噺閰嶇疆
- 鉁?閰嶇疆妫€鏌ュ伐鍏?- 鉁?蹇€熷惎鍔ㄨ剼鏈?
### 4. 鏂囨。
- 鉁?README.md - 瀹屾暣閰嶇疆鎸囧崡
- 鉁?QUICKSTART.md - 5 鍒嗛挓蹇€熷紑濮?- 鉁?.env.example - 閰嶇疆绀轰緥

---

## 鈿狅笍 寰呭畬鎴愭楠わ紙闇€瑕佷綘鍦ㄩ涔﹀悗鍙版搷浣滐級

### 绗?1 姝ワ細鑾峰彇搴旂敤鍑瘉

1. 鐧诲綍 [椋炰功寮€鍙戣€呭悗鍙癩(https://open.feishu.cn/app)
2. 鍒涘缓鎴栭€夋嫨浼佷笟鑷缓搴旂敤
3. 杩涘叆 **鍑瘉涓庡熀纭€淇℃伅** > **搴旂敤鍑瘉**
4. 澶嶅埗 **App ID** 鍜?**App Secret**

---

### 绗?2 姝ワ細濉叆閰嶇疆鏂囦欢

鎵撳紑 `integrations/feishu/.env` 鏂囦欢锛屽～鍏ワ細

```env
APP_ID=cli_xxxxxxxxxxxxxxxxx
APP_SECRET=xxxxxxxxxxxxxxxxxxxxx
LOG_LEVEL=DEBUG
```

---

### 绗?3 姝ワ細閰嶇疆浜嬩欢璁㈤槄

1. 鍦ㄩ涔﹀悗鍙帮紝杩涘叆 **浜嬩欢涓庡洖璋?* > **浜嬩欢閰嶇疆**
2. 缂栬緫璁㈤槄鏂瑰紡锛岄€夋嫨 **浣跨敤闀胯繛鎺ユ帴鏀朵簨浠?*
3. 娣诲姞浜嬩欢锛歚im.message.receive_v1` (鎺ユ敹娑堟伅 v2.0)
4. 淇濆瓨閰嶇疆

鈿狅笍 **娉ㄦ剰**: 濡傛灉淇濆瓨澶辫触锛岃鍏堝惎鍔ㄦ湰鍦板鎴风锛堣绗?4 姝ワ級

---

### 绗?4 姝ワ細鍚姩娴嬭瘯

```bash
# 鏂瑰紡 1: 浣跨敤鍚姩鑴氭湰
cd integrations/feishu
start.bat

# 鏂瑰紡 2: 鐩存帴杩愯
python feishu_bot.py
```

**鎴愬姛鏍囧織**:
```
馃尶 姝ｅ湪杩炴帴椋炰功闀胯繛鎺?..
鈿狅笍 鎸?Ctrl+C 鍋滄鏈嶅姟
connected to wss://xxxxx
```

---

## 馃И 娴嬭瘯鏂规硶

1. 鍦ㄩ涔︿腑鎵惧埌浣犵殑搴旂敤
2. 鍙戦€佹秷鎭細"浣犲ソ"
3. 鏌ョ湅鎺у埗鍙拌緭鍑猴細

```
[鏀跺埌娑堟伅 v2.0], data: {
    "event": {
        "message": {
            "chat_id": "oc_xxxxx",
            "content": "{\"text\":\"浣犲ソ\"}"
        },
        "sender": {
            "sender_id": {
                "user_id": "xxxxx"
            }
        }
    }
}
```

---

## 馃敡 閰嶇疆妫€鏌ュ伐鍏?
杩愯閰嶇疆妫€鏌ワ細

```bash
cd integrations/feishu
python check_config.py
```

**妫€鏌ラ」鐩?*:
- 鉁?鐜鍙橀噺閰嶇疆
- 鉁?SDK 瀹夎鐘舵€?- 鉁?渚濊禆瀹夎鐘舵€?- 鉁?鏂囦欢缁撴瀯瀹屾暣鎬?
---

## 馃摑 鏍稿績浠ｇ爜璇存槑

### 浜嬩欢澶勭悊鍣?
```python
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p1_customized_event("im.message.receive_v1", do_message_event) \
    .build()
```

- `builder("", "")` - 涓や釜鍙傛暟蹇呴』濉┖瀛楃涓?- `register_p2_im_message_receive_v1` - v2.0 鎺ユ敹娑堟伅浜嬩欢
- `register_p1_customized_event` - v1.0 鑷畾涔変簨浠?
### 闀胯繛鎺ュ鎴风

```python
cli = lark.ws.Client(
    APP_ID, 
    APP_SECRET,
    event_handler=event_handler,
    log_level=getattr(lark.LogLevel, LOG_LEVEL, lark.LogLevel.DEBUG)
)
cli.start()  # 闃诲杩愯
```

---

## 鈿狅笍 娉ㄦ剰浜嬮」

1. **闀胯繛鎺ヤ粎鏀寔浼佷笟鑷缓搴旂敤** - 鍟嗗簵搴旂敤闇€鐢?Webhook 妯″紡
2. **3 绉掑唴澶勭悊瀹屾垚** - 瓒呮椂浼氬鑷撮噸鎺?3. **鏈€澶?50 涓繛鎺?* - 姣忎釜搴旂敤鏈€澶?50 涓暱杩炴帴
4. **闆嗙兢妯″紡** - 澶氬鎴风閮ㄧ讲鏃讹紝娑堟伅鍙闅忔満涓€涓鎴风鏀跺埌
5. **鏃犻渶鍏綉 IP** - 鍙渶鏈湴鑳借闂叕缃?
---

## 馃殌 涓嬩竴姝ユ墿灞?
### 瀹炵幇鑷姩鍥炲

鍦?`do_p2_im_message_receive_v1` 鍑芥暟涓坊鍔狅細

```python
# 鍒涘缓瀹㈡埛绔?cli = lark.Client(APP_ID, APP_SECRET)

# 鍙戦€佸洖澶?cli.im.v1.message.create(
    params={"receive_id_type": "chat_id"},
    data={
        "receive_id": message.chat_id,
        "msg_type": "text",
        "content": lark.JSON.marshal({"text": "鏀跺埌浣犵殑娑堟伅锛?})
    }
)
```

### 娣诲姞鏇村浜嬩欢

```python
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .register_p2_member_union_changed(do_member_changed) \  # 鎴愬憳鍙樻洿
    .register_p2_chat_update(do_chat_update) \              # 缇ょ粍鍙樻洿
    .build()
```

---

## 馃摎 鍙傝€冩枃妗?
- [QUICKSTART.md](QUICKSTART.md) - 5 鍒嗛挓蹇€熷紑濮?- [README.md](README.md) - 瀹屾暣閰嶇疆鎸囧崡
- [椋炰功 SDK 鏂囨。](https://open.feishu.cn/document/ukTMukTMukTM/uETO1YjLxkTN24SM5UjN)
- [浜嬩欢璁㈤槄鎸囧崡](https://open.feishu.cn/document/server-docs/event-subscription-guide/overview)
- [浜嬩欢鍒楄〃](https://open.feishu.cn/document/server-docs/event-subscription-guide/event-list)
- [闀胯繛鎺ラ厤缃渚媇(https://open.feishu.cn/document/server-docs/event-subscription-guide/event-subscription-configure-/request-url-configuration-case)

---

## 馃搳 閰嶇疆鐘舵€?
| 椤圭洰 | 鐘舵€?|
|------|------|
| SDK 瀹夎 | 鉁?瀹屾垚 |
| 椤圭洰缁撴瀯 | 鉁?瀹屾垚 |
| 涓荤▼搴?| 鉁?瀹屾垚 |
| 閰嶇疆鏂囦欢 | 鈿狅笍 寰呭～鍏ュ嚟璇?|
| 椋炰功鍚庡彴閰嶇疆 | 鈴?寰呮搷浣?|
| 闀胯繛鎺ユ祴璇?| 鈴?寰呭惎鍔?|

---

**閰嶇疆瀹屾垚** | 2026-03-11 16:50 | 馃尶

涓嬩竴姝ワ細鎵撳紑 `integrations/feishu/.env` 濉叆浣犵殑 App ID 鍜?App Secret锛岀劧鍚庤繍琛?`python feishu_bot.py`

