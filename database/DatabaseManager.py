from typing import List
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db, firestore
import firebase_admin.firestore
import numpy as np
import hashlib
import streamlit as st

from dataclasses import dataclass
from datetime import datetime

@dataclass
class JumpData:
    jump_id : int
    training_id : int
    jump_type : int
    jump_rotations : float
    jump_success : bool
    jump_time : int
    jump_length : float
    jump_max_speed : float

    def to_dict(self):
        return {"training_id" : self.training_id,
        "jump_type" : self.jump_type,
        "jump_rotations" : self.jump_rotations,
        "jump_success" : self.jump_success,
        "jump_time" : self.jump_time,
        "jump_length" : self.jump_length,
        "jump_max_speed" : self.jump_max_speed}
    

@dataclass
class TrainingData:
    training_id : int
    skater_id : int
    training_date : datetime
    dot_id : str
    training_jumps : List[JumpData]

    def to_dict(self):
        return {"skater_id" : self.skater_id,
         "training_date" : self.training_date,
         "dot_id" : self.dot_id,
         "training_jumps" : self.training_jumps}

@dataclass
class SkaterData:
    skater_id : int
    skater_name : str

    def to_dict(self):
        return {"skater_name" : self.skater_name}

class DatabaseManager:
    def __init__(self):
        cred = credentials.Certificate('s2m-skating-firebase-adminsdk-3ofmb-59e6c86f3e.json')
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def save_skater_data(self, data : SkaterData) -> int:
        add_time, new_ref = self.db.collection("skaters").add(data.to_dict())
        return new_ref.id
    
    def save_training_data(self, data : TrainingData) -> int:
        add_time, new_ref = self.db.collection("trainings").add(data.to_dict())
        return new_ref.id
    
    def save_jump_data(self, data : JumpData) -> int:
        add_time, new_ref = self.db.collection("jumps").add(data.to_dict())
        return new_ref.id

    def load_skater_data(self, skater_id : int) -> list[TrainingData]:
        data_trainings = []
        for training in self.db.collection("trainings").where(filter=firestore.firestore.FieldFilter("skater_id", "==", skater_id)).order_by("training_date").stream():
            data_trainings.append(TrainingData(training.id, training.get("skater_id"), training.get("training_date"), 0))
        return data_trainings

    def load_training_data(self, training_id : int) -> list[JumpData]:
        data_jumps = []
        for jump in self.db.collection("jumps").where(filter=firestore.firestore.FieldFilter("training_id", "==", training_id)).order_by("jump_time").stream():
            data_jumps.append(JumpData(jump.id, jump.get("training_id"), jump.get("jump_type"), jump.get("jump_rotations"), jump.get("jump_success"), jump.get("jump_time")))
        return data_jumps
    
    def get_skater_from_training(self, training_id : str) -> int:
        skater_id = self.db.collection("trainings").document(training_id).get().get("skater_id")
        return str(skater_id)

    def get_skater_name_from_id(self, skater_id : str) -> str:
        skater_name = self.db.collection("users").document(skater_id).get().get("name")
        return skater_name

    def get_skater_id_from_name(self, skater_name : str) -> str:
        skater_id  = self.db.collection("skaters").where(filter=firestore.firestore.FieldFilter("skater_name", "==", skater_name)).get()
        return skater_id
    
    def get_all_skaters(self) -> list[SkaterData]:
        data_skaters = []
        for skater in self.db.collection("users").stream():
            if skater.get("role") == "ATHLETE":
                data_skaters.append(SkaterData(skater.id, skater.get("name")))
        return data_skaters

    def get_all_skaters_from_access(self, access) -> list[SkaterData]:
        data_skaters = []
        for skater in self.db.collection("users").stream():
            if skater.get("role") == "ATHLETE" and skater.id in access:
                data_skaters.append(SkaterData(skater.id, skater.get("name")))
        return data_skaters
    
    def get_all_skaters_name(self) -> list[str]:
        data_skaters = []
        for skater in self.db.collection("skaters").stream():
            data_skaters.append(skater.get("skater_name"))
        return data_skaters
    
    def delete_skater_data(self, skater_id : int) -> None:
        self.db.collection("skaters").document(skater_id).delete()

    def find_training(self, date, device_id):
        trainings = self.db.collection("trainings").where(filter=firestore.firestore.FieldFilter("training_date", "==", date)).where(filter=firestore.firestore.FieldFilter("dot_id", "==", device_id)).get()
        return trainings
    
    def set_training_date(self, training_id, date) -> None:
        self.db.collection("trainings").document(training_id).update({"training_date" : date})

    def set_current_record(self, device_id, current_record) -> None:
        self.db.collection("dots").document(device_id).update({"current_record" : current_record})

    def get_current_record(self, device_id) -> str:
        return self.db.collection("dots").document(device_id).get().get("current_record")
    
    def get_bluetooth_address(self, device_list) -> List[str]:
        bluetooth_list = []
        for device in device_list:
            bluetooth_list.append(self.db.collection("dots").document(device).get().get("bluetooth_address"))
        return bluetooth_list
    
    def check_if_user_exists_by_email(self, email) -> bool:
        user_ref = self.db.collection("users").where("email", "==", email).limit(1)
        docs = user_ref.stream()
        for doc in docs:
            return True
        return False
        
    def create_user(self, email, password, role, name, access, coaches) -> None:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        new_user = {
            "email": email,
            "password": hashed_password,
            "role": role,
            "name": name,
            "access": access,
            "coaches": coaches,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP
        }
        add_time, new_ref = self.db.collection("users").add(new_user)
        return new_ref.id


    def get_user_by_email(self, email) -> dict:
        user_ref = self.db.collection("users").where("email", "==", email).limit(1)
        docs = user_ref.stream()
        for doc in docs:
            return doc.to_dict()
        return None
    
    def get_all_coaches_name(self) -> List[str]:
        # Get the list of users with the role "COACH" and return their names
        coaches = self.db.collection("users").where("role", "==", "COACH").stream()
        return [coach.get("name") for coach in coaches]
    
    def give_self_access(self, athlete_name) -> None:
        # Give the athlete access to their own data
        athlete = self.db.collection("users").where("name", "==", athlete_name).get()
        athlete_id = athlete[0].id
        athlete = self.db.collection("users").document(athlete_id)
        athlete.update({"access": firestore.ArrayUnion([athlete_id])})
    
    def add_athlete_to_coach_access(self, coach_name, athlete_name) -> None:
        # Add the athlete's id to the coach's list of athletes
        coach_id = self.db.collection("users").where("name", "==", coach_name).get()
        coach_id = coach_id[0].id
        coach = self.db.collection("users").document(coach_id)
        athlete = self.db.collection("users").where("name", "==", athlete_name).get()
        athlete_id = athlete[0].id
        coach.update({"access": firestore.ArrayUnion([athlete_id])})

    def update_coaches(self, updated_coaches, athlete_name) -> None:
        # Update the list of coaches for the athlete
        athlete = self.db.collection("users").where("name", "==", athlete_name).get()
        athlete_id = athlete[0].id
        athlete = self.db.collection("users").document(athlete_id)
        athlete.update({"coaches": updated_coaches})

    def get_all_trainings_for_skater(self, skater_id) -> List[TrainingData]:
        trainings = self.db.collection("trainings").where("skater_id", "==", skater_id).stream()
        return [TrainingData(training.id, training.get("skater_id"), training.get("training_date"), training.get("dot_id"), training.get("training_jumps")) for training in trainings]

    def get_jump_by_id(self, jump_id: str) -> JumpData:

        jump_doc = self.db.collection("jumps").document(jump_id).get()
        
        if jump_doc.exists:
            jump_data = jump_doc.to_dict()
            return JumpData(
                jump_id=jump_id,
                training_id=jump_data["training_id"],
                jump_type=jump_data["jump_type"],
                jump_rotations=jump_data["jump_rotations"],
                jump_success=jump_data["jump_success"],
                jump_time=jump_data["jump_time"],
                jump_length=jump_data["jump_length"],
                jump_max_speed=jump_data["jump_max_speed"]
            )
        else:
            raise ValueError(f"Aucun jump trouvé avec l'identifiant {jump_id}")
        
    def get_training_from_date(self, date, skater_name) -> int:
        skater_id = self.get_skater_id_from_name(skater_name)
        skater_id = skater_id[0].id
        training = self.db.collection("trainings").where("training_date", "==", date).where("skater_id", "==", skater_id).get()
        return training.id
    
    def update_training_skater_id(self, training_id, skater_id) -> None:
        self.db.collection("trainings").document(training_id).update({"skater_id" : skater_id})

    def get_skater_name_from_training_id(self, training_id) -> str:
        skater_id = self.get_skater_from_training(training_id)
        skater_name = self.get_skater_name_from_id(skater_id)
        return skater_name
    
    def get_training_date_from_training_id(self, training_id) -> datetime:
        training_date = self.db.collection("trainings").document(training_id).get().get("training_date")
        return training_date