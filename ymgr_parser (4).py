import requests
import json

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
        """
        פענוח קובץ ApprovalAll.ymgr בשלוחה מסוימת
        :param extension_number: מספר השלוחה
        """
        if not self.token:
            print("נא להתחבר תחילה!")
            return None

        try:
            # הנתיב המדויק לקובץ ApprovalAll.ymgr
            file_path = f"ivr2:{extension_number}/ApprovalAll.ymgr"
            
            # שימוש בפרמטר 'wath' כפי שהשרת מצפה
            params = {
                'token': self.token,
                'wath': file_path,  # שינוי מ-'what' ל-'wath'
                'convertType': 'json',
                'notLoadLang': 0,
                'renderLanguage': 'HE'
            }
            
            print(f"שולח בקשה לקובץ: {file_path}")
            print(f"פרמטרים: {params}")
            
            response = requests.get(f"{self.base_url}RenderYMGRFile", params=params)
            print(f"URL מלא: {response.url}")
            
            try:
                data = response.json()
                print(f"תגובת השרת: {data}")
                
                if data.get("responseStatus") == "OK":
                    return data.get("data", [])
                else:
                    error_msg = data.get('message', 'שגיאה לא ידועה')
                    print(f"שגיאה בתגובת השרת: {error_msg}")
                    
                    # אם הנתיב לא נכון, ננסה אפשרות אחרת
                    if "file does not exist" in str(error_msg).lower():
                        alternative_path = f"ivr2:/7/ApprovalAll.ymgr"
                        print(f"מנסה נתיב חלופי: {alternative_path}")
                        params['wath'] = alternative_path
                        response = requests.get(f"{self.base_url}RenderYMGRFile", params=params)
                        data = response.json()
                        if data.get("responseStatus") == "OK":
                            return data.get("data", [])
                    return None
                    
            except json.JSONDecodeError:
                print("תוכן התגובה:", response.text[:200])
                return None
                
        except Exception as e:
            print(f"שגיאה בפענוח קובץ YMGR: {str(e)}")
            return None

    def display_approval_data(self, data):
        """
        הצגת נתוני האישורים בצורה מסודרת
        """
        if not data:
            print("אין נתונים להצגה")
            return

        print("\n=== נתוני אישורים ===")
        for record in data:
            print("\nרשומה:")
            for key, value in record.items():
                print(f"{key}: {value}")
            print("-" * 50)

def main():
    # יצירת חיבור למערכת
    api = YemotAPI("0747098744", "123456")  # החלף במספר המערכת והסיסמא שלך
    
    # התחברות
    if not api.login():
        print("ההתחברות נכשלה")
        return
        
    print("התחברות הצליחה!")
    
    # פענוח קובץ ApprovalAll.ymgr בשלוחה 7
    parsed_data = api.parse_ymgr_file("7")
    
    if parsed_data:
        # הצגת הנתונים בצורה מסודרת
        api.display_approval_data(parsed_data)
        
        # שמירת הנתונים לקובץ JSON
        try:
            with open('approval_data.json', 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            print("\nהנתונים נשמרו בהצלחה לקובץ approval_data.json")
        except Exception as e:
            print(f"\nשגיאה בשמירת הקובץ: {str(e)}")

if __name__ == "__main__":
    main()