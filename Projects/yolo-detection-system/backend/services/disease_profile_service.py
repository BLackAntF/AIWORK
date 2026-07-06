from models import DiseaseProfile


class DiseaseProfileService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_by_class_id(self, class_id):
        return DiseaseProfile.query.filter_by(
            class_id=class_id,
            is_active=True
        ).first()

    def get_by_disease_id(self, disease_id):
        return DiseaseProfile.query.filter_by(
            disease_id=disease_id,
            is_active=True
        ).first()

    def get_all(self):
        return DiseaseProfile.query.filter_by(is_active=True).all()

    def get_profile_for_llm(self, class_id):
        profile = self.get_by_class_id(class_id)
        if not profile:
            return None
        return {
            "disease_name": profile.disease_name,
            "causes": profile.causes,
            "symptoms": profile.symptoms,
            "prevention": profile.prevention,
            "treatment": profile.treatment,
            "pesticides": profile.pesticides
        }


disease_profile_service = DiseaseProfileService()
