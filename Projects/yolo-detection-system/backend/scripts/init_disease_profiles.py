import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from app import create_app
from extensions import db

DISEASE_DATA = [
    {"disease_id": "BacterialSpot", "disease_name": "细菌性斑点病", "class_id": 0, "causes": "由黄单胞杆菌属细菌引起。病原菌在病残体或种子上越冬，通过雨水、灌溉水、昆虫及农事操作传播。高温高湿条件利于发病。", "symptoms": "叶片出现水渍状小斑点，逐渐扩大成褐色或黑色斑点，病斑周围有黄色晕圈。茎部出现褐色条斑。果实出现稍微隆起的小斑点，后期病斑龟裂。", "occurrence": "雨季或露水多的季节发病重。种植过密、通风不良加重发病。", "prevention": "1. 选用抗病品种；2. 种子消毒（55°C温水浸种30分钟）；3. 合理密植，加强通风；4. 避免大水漫灌；5. 及时清除病残体。", "treatment": "发病初期喷施77%氢氧化铜可湿性粉剂500倍液或72%农用硫酸链霉素可溶性粉剂4000倍液，每隔7-10天一次，连续2-3次。", "pesticides": "77%氢氧化铜可湿性粉剂（500倍）、72%农用硫酸链霉素可溶性粉剂（4000倍）、47%春雷霉素·王铜可湿性粉剂（800倍）", "is_active": True},
    {"disease_id": "EarlyBlight", "disease_name": "早疫病", "class_id": 1, "causes": "由半知菌亚门链格孢属真菌引起。病原菌可在病残体或种子表面越冬，通过气流、雨水传播。高温高湿（25-30°C，相对湿度80%以上）利于发病。", "symptoms": "叶片初期出现暗褐色或黑色小斑点，逐渐扩大成圆形或不规则形病斑，直径3-12mm。病斑有同心轮纹，中央产生黑色霉层。严重时叶片枯黄脱落。", "occurrence": "结果期发病最重。一般春播番茄在6-8月发病严重。种植过密、通风不良、排水不畅田块发病重。", "prevention": "1. 选用抗病品种；2. 实行轮作（与非茄科作物轮作2-3年）；3. 合理密植，加强通风；4. 科学施肥，增施磷钾肥；5. 及时清除病残体。", "treatment": "发病初期喷施75%百菌清可湿性粉剂600倍液、25%嘧菌酯悬浮剂1500倍液或43%戊唑醇悬浮剂3000倍液，每隔7-10天一次，连续2-3次。", "pesticides": "75%百菌清可湿性粉剂（600倍）、25%嘧菌酯悬浮剂（1500倍）、43%戊唑醇悬浮剂（3000倍）、10%苯醚甲环唑水分散粒剂（2000倍）", "is_active": True},
    {"disease_id": "Healthy", "disease_name": "健康叶片", "class_id": 2, "causes": "无病害，植株生长健康。", "symptoms": "叶片呈绿色或深绿色，叶片完整，无病斑、无黄化、无畸形，光合作用正常。", "occurrence": "正常生长状态，无需防治。", "prevention": "继续保持良好栽培管理：合理浇水施肥、加强通风透光、及时防治病虫害。", "treatment": "无需治疗，继续保持良好管理即可。", "pesticides": "无需使用任何药剂。", "is_active": True},
    {"disease_id": "LateBlight", "disease_name": "晚疫病", "class_id": 3, "causes": "由鞭毛菌亚门疫霉属真菌引起。病原菌在病残体或马铃薯块茎中越冬，通过气流、雨水传播。低温高湿（10-25°C，多雨雾）利于发病。", "symptoms": "叶片出现大型暗绿色水渍状病斑，边缘不明显。潮湿时病斑表面产生白色霉层。茎部出现黑褐色条斑，稍凹陷。果实出现灰褐色病斑，稍硬化。", "occurrence": "昼夜温差大、夜间露水重时发病严重。洼地、排水不良田块发病重。是一种毁灭性的病害。", "prevention": "1. 选用抗病品种；2. 高垄栽培，合理密植；3. 加强通风透光，降低湿度；4. 避免偏施氮肥；5. 发现病株立即拔除。", "treatment": "发病初期立即喷药，可选用银法利（氟吡菌胺·霜霉威）悬浮剂600倍液、72%霜脲氰·锰锌可湿性粉剂600倍液或68%精甲霜灵·锰锌水分散粒剂800倍液，每隔5-7天一次。", "pesticides": "银法利悬浮剂（600倍）、72%霜脲氰·锰锌可湿性粉剂（600倍）、68%精甲霜灵·锰锌水分散粒剂（800倍）、72.2%霜霉威盐酸盐水剂（800倍）", "is_active": True},
    {"disease_id": "LeafMold", "disease_name": "叶霉病", "class_id": 4, "causes": "由半知菌亚门枝孢属真菌引起。病原菌在病残体上越冬，通过气流传播。高温高湿（20-25°C，相对湿度90%以上）利于发病。", "symptoms": "叶片正面出现淡黄色褪绿斑，叶背面出现灰白色或紫灰色霉层，后期霉层颜色加深呈褐色。严重时叶片向上卷曲，果实发育不良。", "occurrence": "保护地栽培发病重，特别是连阴雨天气、通风不良、浇水过多时发病严重。", "prevention": "1. 选用抗病品种；2. 加强通风换气，降低棚内湿度；3. 合理浇水，避免大水漫灌；4. 及时摘除病叶；5. 实行轮作。", "treatment": "发病初期喷施47%春雷霉素·王铜可湿性粉剂800倍液、10%多抗霉素可湿性粉剂1000倍液或70%甲基硫菌灵可湿性粉剂800倍液，每隔7-10天一次。", "pesticides": "47%春雷霉素·王铜可湿性粉剂（800倍）、10%多抗霉素可湿性粉剂（1000倍）、70%甲基硫菌灵可湿性粉剂（800倍）、50%扑海因可湿性粉剂（1000倍）", "is_active": True},
    {"disease_id": "MosaicVirus", "disease_name": "花叶病毒病", "class_id": 5, "causes": "由烟草花叶病毒（TMV）或黄瓜花叶病毒（CMV）引起。病原体主要通过汁液接触传播，也可通过蚜虫传播。高温干旱利于蚜虫繁殖和病毒传播。", "symptoms": "叶片出现深浅相间的花叶状斑驳，叶片皱缩不平，向上卷曲。严重时叶片呈柳叶状，果实变小畸形，产量显著下降。", "occurrence": "春茬和秋茬发病较重。管理粗放、杂草丛生、蚜虫多的田块发病重。", "prevention": "1. 选用抗病品种；2. 种子消毒（10%磷酸三钠溶液浸种20分钟）；3. 避免与烟草作物邻作；4. 及时防治蚜虫；5. 操作时避免汁液传播。", "treatment": "目前无特效药剂，以预防为主。发病后可喷施0.5%菇类蛋白多糖水剂300倍液或20%病毒A可湿性粉剂500倍液控制病情蔓延，同时加强肥水管理。", "pesticides": "0.5%菇类蛋白多糖水剂（300倍）、20%病毒A可湿性粉剂（500倍）、1.5%植病灵乳剂（1000倍）、5%菌毒清水剂（200倍）", "is_active": True},
    {"disease_id": "SeptoriaLeafSpot", "disease_name": "斑枯病", "class_id": 6, "causes": "由半知菌亚门壳针孢属真菌引起。病原菌在病残体上越冬，通过雨水、昆虫传播。温暖高湿（22-26°C，多雨）利于发病。", "symptoms": "叶片出现圆形或近圆形小斑点，直径2-4mm，灰白色，边缘深褐色，病斑表面散生许多黑色小点（分生孢子器）。严重时叶片枯黄脱落。", "occurrence": "春播番茄在6-7月发病重。植株生长衰弱、偏施氮肥田块发病重。", "prevention": "1. 实行3年以上轮作；2. 合理施肥，增施磷钾肥；3. 及时清除病残体；4. 合理密植，加强通风透光。", "treatment": "发病初期喷施50%百菌通可湿性粉剂500倍液、70%甲基硫菌灵可湿性粉剂800倍液或64%杀毒矾可湿性粉剂500倍液，每隔7-10天一次。", "pesticides": "50%百菌通可湿性粉剂（500倍）、70%甲基硫菌灵可湿性粉剂（800倍）、64%杀毒矾可湿性粉剂（500倍）、58%甲霜灵·锰锌可湿性粉剂（500倍）", "is_active": True},
    {"disease_id": "SpiderMites", "disease_name": "蜘蛛螨危害", "class_id": 7, "causes": "由朱砂叶螨等螨类引起。以成螨和若螨在叶片背面刺吸汁液。高温干燥（28-30°C，相对湿度35-55%）利于繁殖。", "symptoms": "叶片正面出现褪绿小斑点，逐渐变黄变白。叶片背面可见螨类活动，严重时叶片枯黄脱落。拉丝结网是重要特征。可造成大幅减产。", "occurrence": "6-8月高温干燥季节发生严重。植株生长衰弱、周围杂草丛生利于发生。", "prevention": "1. 及时清除杂草，减少虫源；2. 加强肥水管理，增强植株抗性；3. 避免过于干燥，保持适宜湿度；4. 避免与豆类、棉作物邻作。", "treatment": "发现螨害时立即喷药，可选用1.8%阿维菌素乳油3000倍液、15%哒螨灵乳油2500倍液或24%螺螨酯悬浮剂4000倍液，重点喷施叶片背面，每隔7天一次，连续2-3次。", "pesticides": "1.8%阿维菌素乳油（3000倍）、15%哒螨灵乳油（2500倍）、24%螺螨酯悬浮剂（4000倍）、20%丁硫克百威乳油（2000倍）", "is_active": True},
    {"disease_id": "TargetSpot", "disease_name": "靶斑病", "class_id": 8, "causes": "由半知菌亚门棒孢属真菌引起。病原菌在病残体上越冬，通过风雨传播。高温高湿（25-30°C，多雨）利于发病。", "symptoms": "叶片出现红褐色圆形病斑，直径3-15mm，病斑有同心轮纹和黄色晕圈，形似靶标。严重时病斑连片，叶片枯黄。茎和果实也可受害。", "occurrence": "6-9月高温多雨季节发病重。种植过密、通风透光差、排水不良田块发病重。", "prevention": "1. 选用抗病品种；2. 实行轮作；3. 合理密植，加强通风透光；4. 增施有机肥和磷钾肥；5. 及时清除病残体。", "treatment": "发病初期喷施40%嘧霉胺悬浮剂1000倍液、50%异菌脲可湿性粉剂1000倍液或25%咪鲜胺乳油1000倍液，每隔7-10天一次，连喷2-3次。", "pesticides": "40%嘧霉胺悬浮剂（1000倍）、50%异菌脲可湿性粉剂（1000倍）、25%咪鲜胺乳油（1000倍）、75%百菌清可湿性粉剂（600倍）", "is_active": True},
    {"disease_id": "YellowLeafCurlVirus", "disease_name": "黄化曲叶病毒病", "class_id": 9, "causes": "由双生病毒科病毒引起。主要通过烟粉虱传播，带毒烟粉虱终身传毒。高温干旱（25-30°C）利于烟粉虱繁殖和病毒传播。", "symptoms": "植株生长缓慢，顶部叶片变小、皱缩、向上卷曲，叶片叶脉间黄化。后期植株明显矮化，花蕾易脱落，坐果困难，果实小而硬。", "occurrence": "夏秋茬发病严重，特别是保护地栽培。烟粉虱发生高峰期（7-9月）与发病高峰期一致。", "prevention": "1. 选用抗病或耐病品种；2. 育苗期使用防虫网隔离；3. 及时防治烟粉虱（悬挂黄板、喷施杀虫剂）；4. 避免与茄科作物邻作；5. 拔除病株。", "treatment": "目前无特效药剂，以预防和控害为主。发现病株立即拔除并销毁，同时喷施杀虫剂防治烟粉虱，防止蔓延。可喷施0.5%菇类蛋白多糖水剂增强植株抗性。", "pesticides": "0.5%菇类蛋白多糖水剂（300倍）、20%病毒A可湿性粉剂（500倍）、25%噻嗪酮可湿性粉剂（1000倍，用于防治烟粉虱）、10%吡虫啉可湿性粉剂（2000倍）", "is_active": True}
]


def init_disease_profiles():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("表创建完成")

        created = 0
        updated = 0
        for data in DISEASE_DATA:
            existing = db.session.execute(
                db.text("SELECT id FROM disease_profiles WHERE disease_id = :disease_id"),
                {"disease_id": data["disease_id"]}
            ).fetchone()

            if existing:
                update_fields = []
                for key, value in data.items():
                    update_fields.append(f"{key} = :{key}")
                update_sql = f"UPDATE disease_profiles SET {', '.join(update_fields)} WHERE disease_id = :disease_id"
                db.session.execute(db.text(update_sql), data)
                updated += 1
            else:
                cols = ", ".join(data.keys())
                vals = ", ".join([f":{k}" for k in data.keys()])
                insert_sql = f"INSERT INTO disease_profiles ({cols}) VALUES ({vals})"
                db.session.execute(db.text(insert_sql), data)
                created += 1

        db.session.commit()
        print(f"病害档案初始化完成：新增 {created} 条，更新 {updated} 条")


if __name__ == '__main__':
    init_disease_profiles()
