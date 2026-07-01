"""
数据库初始化脚本

使用方法:
    python init_db.py
"""
from app import create_app
from extensions import db
from models import User, Knowledge, SystemConfig, ModelInfo, KnowledgeCategory


def init_database():
    """初始化数据库"""
    app = create_app()

    with app.app_context():
        # 创建所有表
        db.create_all()
        print("=== 数据库表创建完成 ===")

        # 创建默认管理员
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("  默认管理员创建成功: admin / admin123")
        else:
            # 确保管理员角色正确
            if admin.role != 'admin':
                admin.role = 'admin'
                print("  管理员角色已修正为 admin")
            else:
                print("  管理员已存在，跳过创建")

        # 创建默认测试用户
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                role='user'
            )
            test_user.set_password('123456')
            db.session.add(test_user)
            print("  测试用户创建成功: testuser / 123456")
        else:
            print("  测试用户已存在，跳过创建")

        # 初始化默认知识分类
        default_categories = [
            {'name': '病害防治', 'description': '植物病害的识别与防治方法'},
            {'name': '养护知识', 'description': '植物日常养护管理知识'},
            {'name': '虫害防治', 'description': '植物虫害的识别与防治方法'}
        ]
        for cat_data in default_categories:
            cat = KnowledgeCategory.query.filter_by(name=cat_data['name']).first()
            if not cat:
                cat = KnowledgeCategory(**cat_data)
                db.session.add(cat)
                print(f"  创建分类: {cat_data['name']}")
        print("  知识分类初始化完成")

        # 初始化一些示例知识库数据
        if Knowledge.query.count() == 0:
            sample_knowledge = [
                {
                    'title': '植物斑点病的识别与防治',
                    'content': '斑点病是植物常见的真菌病害，主要表现为叶片上出现圆形或不规则形的褐色斑点，严重时叶片枯黄脱落。防治方法：1. 及时清除病叶并集中销毁；2. 保持通风透光，降低湿度；3. 发病初期喷施多菌灵、百菌清等杀菌剂，每隔7-10天一次，连续2-3次。',
                    'category': '病害防治',
                    'source': '植物病害防治手册'
                },
                {
                    'title': '白粉病的症状与治疗',
                    'content': '白粉病由白粉菌引起，在叶片、嫩茎上形成白色粉状霉层。后期病斑变褐色，叶片卷曲枯黄。防治措施：1. 加强栽培管理，合理密植；2. 发病初期用三唑酮、戊唑醇等药剂喷雾；3. 注意氮磷钾配合施用，避免偏施氮肥。',
                    'category': '病害防治',
                    'source': '园艺技术指南'
                },
                {
                    'title': '锈病的识别特征与防治',
                    'content': '锈病主要危害叶片，发病初期出现黄色小斑点，后扩大成圆形或椭圆形的橙黄色疱斑，破裂后散出铁锈色粉末。防治方法：1. 清除转主寄主和病残体；2. 合理施肥，增强植株抗病性；3. 发病初期喷施粉锈宁、代森锰锌等药剂。',
                    'category': '病害防治',
                    'source': '农业技术推广站'
                },
                {
                    'title': '灰霉病的发生规律及防治',
                    'content': '灰霉病是由灰葡萄孢菌引起的真菌病害，主要危害花、果、叶。低温高湿环境下易发病。防治要点：1. 控制湿度，加强通风；2. 及时清除病花病果；3. 发病初期喷施腐霉利、异菌脲、嘧霉胺等药剂；4. 注意轮换用药，防止抗药性。',
                    'category': '病害防治',
                    'source': '植物保护手册'
                },
                {
                    'title': '炭疽病的诊断与防治技术',
                    'content': '炭疽病主要危害叶片和果实。叶片受害后产生圆形或近圆形褐色病斑，边缘稍隆起，中央灰白色，后期病斑上产生小黑点。防治方法：1. 选用抗病品种；2. 清除病残体，减少菌源；3. 发病初期喷施咪鲜胺、苯醚甲环唑、代森联等药剂。',
                    'category': '病害防治',
                    'source': '植物病理学教材'
                },
                {
                    'title': '健康植物的养护要点',
                    'content': '保持植物健康的关键：1. 合理浇水：见干见湿，避免积水；2. 适当光照：根据植物习性安排光照时间；3. 科学施肥：氮磷钾平衡，生长期多施氮肥，花果期增施磷钾肥；4. 定期修剪：保持通风透光；5. 病虫害预防：定期检查，早发现早防治。',
                    'category': '养护知识',
                    'source': '园艺入门指南'
                }
            ]

            for item in sample_knowledge:
                kb = Knowledge(**item)
                db.session.add(kb)

            print(f"  初始化 {len(sample_knowledge)} 条示例知识库数据")
        else:
            print("  知识库已有数据，跳过初始化")

        # 初始化系统配置
        default_configs = [
            {'config_key': 'yolo_conf_threshold', 'config_value': '0.5', 'description': 'YOLO 置信度阈值'},
            {'config_key': 'yolo_iou_threshold', 'config_value': '0.45', 'description': 'YOLO IOU 阈值'},
            {'config_key': 'max_upload_size', 'config_value': '10', 'description': '最大上传文件大小（MB）'},
            {'config_key': 'site_name', 'config_value': 'YOLO 目标检测系统', 'description': '站点名称'},
            {'config_key': 'enable_registration', 'config_value': 'true', 'description': '是否允许用户注册'}
        ]
        for cfg_data in default_configs:
            cfg = SystemConfig.query.filter_by(config_key=cfg_data['config_key']).first()
            if not cfg:
                cfg = SystemConfig(**cfg_data)
                db.session.add(cfg)
                print(f"  创建配置: {cfg_data['config_key']} = {cfg_data['config_value']}")
        print("  系统配置初始化完成")

        # 初始化默认模型记录
        default_model = ModelInfo.query.filter_by(name='默认模型').first()
        if not default_model:
            model = ModelInfo(
                name='默认模型',
                path='./models/default.pt',
                version='v1.0',
                is_active=True,
                description='系统默认 YOLOv8 模型（Mock）'
            )
            db.session.add(model)
            print("  默认模型创建成功")
        else:
            print("  默认模型已存在，跳过创建")

        db.session.commit()
        print("\n=== 数据库初始化完成 ===")


if __name__ == '__main__':
    init_database()
