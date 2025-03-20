import requests
import json
import os
from datetime import datetime

class YemotAPI:
    def __init__(self, system_number, password):
        self.base_url = "https://www.call2all.co.il/ym/api/"
        self.system_number = system_number
        self.password = password
        self.token = None

    def login(self):
        try:
            params = {
                'username': self.system_number,
                'password': self.password
            }
            
            response = requests.get(f"{self.base_url}Login", params=params)
            data = response.json()
            print("תגובת התחברות:", data)
            
            if data.get("responseStatus") == "OK":
                self.token = data.get("token")
                return True
            return False
            
        except Exception as e:
            print(f"שגיאה בהתחברות: {str(e)}")
            return False

    def parse_ymgr_file(self, extension_number):
        if not self.token:
            print("נא להתחבר תחילה!")
            return None

        try:
            file_path = f"ivr2:{extension_number}/ApprovalAll.ymgr"
            
            params = {
                'token': self.token,
                'wath': file_path,
                'convertType': 'json',
                'notLoadLang': 0,
                'renderLanguage': 'HE'
            }
            
            print(f"שולח בקשה לקובץ: {file_path}")
            
            response = requests.get(f"{self.base_url}RenderYMGRFile", params=params)
            
            try:
                data = response.json()
                if data.get("responseStatus") == "OK":
                    return data.get("data", [])
                else:
                    print(f"שגיאה בתגובת השרת: {data}")
                    return None
                    
            except json.JSONDecodeError:
                print("תוכן התגובה:", response.text[:200])
                return None
                
        except Exception as e:
            print(f"שגיאה בפענוח קובץ YMGR: {str(e)}")
            return None

def main():
    # יצירת חיבור למערכת
    api = YemotAPI("0747098744", "123456")
    
    if not api.login():
        print("ההתחברות נכשלה")
        return
        
    print("התחברות הצליחה!")
    
    # פענוח קובץ ApprovalAll.ymgr בשלוחה 7
    parsed_data = api.parse_ymgr_file("7")
    
    if parsed_data:
        # הוספת מידע על זמן השליפה לנתונים
        data_with_metadata = {
            "fetch_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            "data": parsed_data
        }
        
        # שמירת הנתונים בקובץ approvals.json בתיקיית הפרויקט
        try:
            # שמירה בקובץ קבוע
            with open('approvals.json', 'w', encoding='utf-8') as f:
                json.dump(data_with_metadata, f, ensure_ascii=False, indent=2)
            print("הנתונים נשמרו בהצלחה לקובץ approvals.json")
            
        except Exception as e:
            print(f"שגיאה בשמירת הקובץ: {str(e)}")

if __name__ == "__main__":
    main()