import requests
from bs4 import BeautifulSoup
import json
import time
import urllib3
import re
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def my_where():
    return r'C:\ProgramData\NetFree\CA\netfree-ca-list.crt'
requests.certs.where = my_where

class YemotAPI:
    def __init__(self, username, password):
        self.base_url = "https://www.call2all.co.il/ym/api/"
        self.username = username
        self.password = password
        self.token = None

    def login(self):
        try:
            response = requests.get(f"{self.base_url}Login", params={
                "username": self.username,
                "password": self.password
            })
            data = response.json()
            print("תגובת התחברות:", data)
            
            if data.get("responseStatus") == "OK":
                self.token = data.get("token")
                return True
            return False
        except Exception as e:
            print(f"שגיאה בהתחברות: {str(e)}")
            return False


            
    def upload_profile_tts(self, text):
        """
        מעלה קובץ TTS עם נתוני הפרופיל
        """
        if not self.token:
            print("נדרשת התחברות תחילה")
            return False

        clean_text = re.sub(r'https?://\S+', '', text)  # ניקוי קישורים
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # ניקוי רווחים מיותרים

        if not clean_text:
            print("אין טקסט להקראה")
            return False

        data = {
            "token": self.token,
            "what": "ivr2:/3/000.tts",  # שם קובץ קבוע לפרופיל
            "contents": clean_text
        }

        try:
            print("מעלה נתוני פרופיל...")
            print(f"תוכן הפרופיל: {clean_text}")
            
            response = requests.post(f"{self.base_url}UploadTextFile", data=data)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('responseStatus') == 'OK':
                    print("נתוני הפרופיל הועלו בהצלחה")
                    return True
                else:
                    print(f"שגיאה בתגובת השרת: {response_data}")
                    return False
            else:
                print(f"שגיאה בהעלאת נתוני הפרופיל: {response.status_code}")
                print(f"תוכן התגובה: {response.text}")
                return False
                
        except Exception as e:
            print(f"שגיאה בהעלאת נתוני הפרופיל: {str(e)}")
            return False

    def upload_tts_file(self, text, index):
        if not self.token:
            print("נדרשת התחברות תחילה")
            return False

        # שימוש בפונקציה המשופרת לניקוי טקסט
        clean_text = clean_text_for_tts(text, index + 1)  # index + 1 כדי שההתראות יתחילו מ-1

        if not clean_text:
            print("אין טקסט להקראה אחרי הניקוי")
            return False

        # יצירת שם קובץ עם המספר הסידורי
        file_name = f"{index:03d}.tts"  # למשל: 000.tts, 001.tts, 002.tts
        
        data = {
            "token": self.token,
            "what": f"ivr2:/1/{file_name}",
            "contents": clean_text
        }

        try:
            print(f"\nמעלה התראה מספר {index + 1}:")
            print(f"שם הקובץ: {file_name}")
            print(f"תוכן ההתראה: {clean_text}")
            
            response = requests.post(f"{self.base_url}UploadTextFile", data=data)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('responseStatus') == 'OK':
                    print(f"התראה {index + 1} הועלתה בהצלחה")
                    return True
                else:
                    print(f"שגיאה בתגובת השרת: {response_data}")
                    return False
            else:
                print(f"שגיאה בהעלאת התראה {index + 1}: {response.status_code}")
                print(f"תוכן התגובה: {response.text}")
                return False
                
        except Exception as e:
            print(f"שגיאה בהעלאת התראה {index + 1}: {str(e)}")
            return False
    
def clean_text_for_tts(text, notification_number=None):
    """
    מנקה ומעבד טקסט להקראה עם שיפורים
    """
    # רק אם יש מספר התראה, נוסיף את הפתיח
    if notification_number is not None:
        text = f"התראה מספר {notification_number}. {text}"
    
    # ניקוי קישורים והחלפתם במילה [קישור]
    text = re.sub(r'https?://\S+', '[קישור]', text)
    
    # ניקוי תמונות והחלפתם במילה [תמונה]
    text = re.sub(r'!\[.*?\]\(.*?\)', '[תמונה]', text)
    
    # ניקוי סיומות קבצים
    text = re.sub(r'\.txt|\.exe|\.rar|\.zip|\.py', '', text)
    
    # ניקוי תווים לא רצויים אבל שמירה על עברית ואנגלית
    text = re.sub(r'[^\u0590-\u05FF\u0020-\u007F\s\.\,\?\!]', '', text)
    
    # הסרת רווחים מיותרים
    text = re.sub(r'\s+', ' ', text).strip()
    
    # טיפול בציטוטים
    text = re.sub(r'> ?', 'ציטוט: ', text)
    
    # הוספת נקודה בסוף אם אין
    if not text.endswith(('.', '!', '?')):
        text += '.'
    
    return text

def get_nodebb_post_content(url):
    """
    מושך תוכן מפוסט של NodeBB באמצעות ה-API
    """
    try:
        username = url.split('/')[-1]
        api_url = f"https://mitmachim.top/api/user/{username}/posts"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(api_url, verify=False, headers=headers)
        data = response.json()
        
        if 'posts' in data:
            all_content = []
            for post in data['posts']:
                if 'content' in post:
                    soup = BeautifulSoup(post['content'], 'html.parser')
                    text = soup.get_text(strip=True)
                    clean_text = clean_text_for_tts(text)
                    if clean_text:
                        all_content.append(clean_text)
            
            return ' '.join(all_content)
        else:
            print("לא נמצא תוכן בתגובת ה-API")
            return None
            
    except Exception as e:
        print(f"שגיאה בקריאת תוכן מ-NodeBB: {str(e)}")
        return None

def split_text_to_chunks(text, max_length=150):
    """
    מחלק טקסט לחלקים קטנים
    """
    sentences = text.split('.')
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if current_length + len(sentence) + 2 <= max_length:
            current_chunk.append(sentence)
            current_length += len(sentence) + 2
        else:
            if current_chunk:
                chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentence]
            current_length = len(sentence)

    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')

    return chunks


class NodeBBAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.base_url = "https://mitmachim.top"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://mitmachim.top',
            'Referer': 'https://mitmachim.top/'
        }
        self.user_data = None

    def login(self, username, password):
        try:
            print("מתחיל תהליך התחברות ישיר דרך ה-API...")
            
            # קבלת config
            config_response = self.session.get(
                f"{self.base_url}/api/config",
                headers=self.headers
            )
            print(f"תגובת config: {config_response.status_code}")
            if config_response.ok:
                config_data = config_response.json()
                print(f"מידע מה-config: {json.dumps(config_data, ensure_ascii=False)[:200]}")
            
            # התחברות
            login_data = {
                "username": username,
                "password": password
            }
            
            print("שולח בקשת התחברות...")
            login_response = self.session.post(
                f"{self.base_url}/api/v3/utilities/login",
                json=login_data,
                headers=self.headers
            )
            
            print(f"קוד תשובה: {login_response.status_code}")
            if login_response.ok:
                response_data = login_response.json()
                print(f"תוכן תגובה: {json.dumps(response_data, ensure_ascii=False)}")
                
                if response_data.get('status', {}).get('code') == 'ok':
                    self.user_data = response_data.get('response', {})
                    print("התחברות הצליחה!")
                    return True

            print("התחברות נכשלה")
            return False
            
        except Exception as e:
            print(f"שגיאה בהתחברות: {str(e)}")
            return False

    def get_notifications(self):
        if not self.user_data:
            print("יש להתחבר תחילה!")
            return None

        try:
            print("מנסה לקבל התראות...")
            
            response = self.session.get(
                f"{self.base_url}/api/notifications",
                headers=self.headers
            )
            
            if response.ok:
                data = response.json()
                if isinstance(data, dict) and 'notifications' in data:
                    notifications = data['notifications']
                elif isinstance(data, list):
                    notifications = data
                else:
                    notifications = []

                print(f"נמצאו {len(notifications)} התראות")
                
                # עיבוד ההתראות לטקסט
                all_content = []
                for notif in notifications:
                    # קבלת שם המשתמש
                    username = notif.get('user', {}).get('username', 'משתמש לא ידוע')
                    notification_type = notif.get('type', '')
                    
                    # קבלת הטקסט של ההתראה והפוסט
                    notification_content = ""
                    post_content = ""
                    
                    # קבלת תוכן ההתראה הקצר (bodyShort)
                    if 'bodyShort' in notif and notif['bodyShort']:
                        notification_content = BeautifulSoup(notif['bodyShort'], 'html.parser').get_text(strip=True)
                    
                    # קבלת תוכן הפוסט המלא (bodyLong)
                    if 'bodyLong' in notif and notif['bodyLong']:
                        post_content = BeautifulSoup(notif['bodyLong'], 'html.parser').get_text(strip=True)
                    
                    # בניית הודעה מותאמת לפי סוג ההתראה
                    notification_text = ""
                    if notification_type == 'upvote':
                        notification_text = f"@{username} הצביע בעד הפוסט שלך"
                    elif notification_type == 'new_reply':
                        notification_text = f"@{username} הגיב לפוסט שלך"
                    elif notification_type == 'follow':
                        notification_text = f"@{username} התחיל לעקוב אחריך"
                    elif notification_type == 'mention':
                        notification_text = f"@{username} הזכיר אותך"
                    elif notification_type == 'quote':
                        notification_text = f"@{username} ציטט את דבריך"
                    elif notification_type == 'new_chat':
                        notification_text = f"@{username} שלח לך הודעה פרטית"
                    elif notification_type == 'group_invite':
                        notification_text = f"@{username} הזמין אותך להצטרף לקבוצה"
                    else:
                        notification_text = notification_content
                    
                    # הוספת תוכן ההודעה אם קיים
                    final_text = notification_text
                    if notification_content and notification_content not in notification_text:
                        final_text += f". תוכן ההתראה: {notification_content}"
                    if post_content and post_content not in final_text:
                        final_text += f". תוכן הפוסט: {post_content}"
                    
                    if final_text:
                        all_content.append(final_text)
                
                if all_content:
                    return all_content
                else:
                    print("לא נמצא טקסט בהתראות")
                    return None
            else:
                print(f"שגיאה בקבלת התראות: {response.status_code}")
                print(f"תוכן התגובה: {response.text[:200]}")
                return None
                
        except Exception as e:
            print(f"שגיאה בקבלת התראות: {str(e)}")
            return None
    def get_user_profile(self, username=None):
        """
        מושך את נתוני הפרופיל של משתמש
        """
        if not self.user_data:
            print("יש להתחבר תחילה!")
            return None

        try:
            print(f"מושך נתוני פרופיל עבור המשתמש: {username}")
            
            # החלפת רווחים במקפים ואז קידוד URL
            from urllib.parse import quote
            formatted_username = username.replace(" ", "-")
            encoded_username = quote(formatted_username)
            
            # שימוש בנתיב הנכון
            response = self.session.get(
                f"{self.base_url}/api/user/{encoded_username}",
                headers=self.headers
            )
            
            print(f"קוד תגובה מהשרת: {response.status_code}")
            print(f"URL שנוסה: {response.url}")
            
            if response.ok:
                data = response.json()
                print(f"התקבלו נתונים: {json.dumps(data, ensure_ascii=False)[:200]}")
                
                # בניית טקסט מובנה מנתוני הפרופיל
                profile_parts = []
                
                # שם המשתמש
                username_display = data.get('username', username)
                profile_parts.append(f"פרופיל המשתמש {username_display}")
                
                # תיאור/חתימה
                if 'aboutme' in data and data['aboutme']:
                    aboutme = BeautifulSoup(data['aboutme'], 'html.parser').get_text(strip=True)
                    if aboutme:
                        profile_parts.append(f"אודות: {aboutme}")
                
                if 'signature' in data and data['signature']:
                    signature = BeautifulSoup(data['signature'], 'html.parser').get_text(strip=True)
                    if signature:
                        profile_parts.append(f"חתימה: {signature}")
                
                # מיקום
                if 'location' in data and data['location']:
                    profile_parts.append(f"מיקום: {data['location']}")
                
                # תאריך הצטרפות
                if 'joindate' in data:
                    from datetime import datetime
                    join_date = datetime.fromtimestamp(int(data['joindate'])/1000).strftime('%d/%m/%Y')
                    profile_parts.append(f"הצטרף בתאריך: {join_date}")
                
                # סטטיסטיקות
                if 'postcount' in data:
                    profile_parts.append(f"מספר פוסטים: {data['postcount']}")
                
                if 'reputation' in data:
                    profile_parts.append(f"מספר נקודות מוניטין: {data['reputation']}")
                
                # עוקבים ועוקב אחרי
                if 'followingCount' in data:
                    profile_parts.append(f"עוקב אחרי: {data['followingCount']} משתמשים")
                
                if 'followerCount' in data:
                    profile_parts.append(f"מספר עוקבים: {data['followerCount']}")
                
                # חיבור כל החלקים לטקסט אחד
                profile_text = ". ".join(profile_parts)
                print(f"טקסט פרופיל מוכן: {profile_text}")
                
                return profile_text
                
            else:
                print(f"שגיאה בקבלת נתוני פרופיל: {response.status_code}")
                print(f"URL שנוסה: {response.url}")
                print(f"תוכן התגובה: {response.text[:200]}")
                return None
            
        except Exception as e:
            print(f"שגיאה בקבלת נתוני פרופיל: {str(e)}")
            return None
    
    def get_user_posts(self, username):
        try:
            response = self.session.get(
                f"{self.base_url}/api/user/{username}/posts",
                headers=self.headers,
                verify=False
            )
            return response.json()
        except Exception as e:
            print(f"שגיאה בקבלת פוסטים: {str(e)}")
            return None

class RecentPostsAPI:
    def __init__(self):
        self.base_url = "https://mitmachim.top"
        self.session = requests.Session()
        self.session.verify = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

    def get_recent_posts(self, limit=10):
        """
        מושך את הפוסטים האחרונים מהפורום
        :param limit: מספר הפוסטים לשליפה
        :return: רשימה של פוסטים מעובדים
        """
        try:
            print(f"מושך {limit} פוסטים אחרונים...")
            
            # שליפת הפוסטים האחרונים מ-API של NodeBB
            response = self.session.get(
                f"{self.base_url}/api/recent/posts",
                params={'count': limit},
                headers=self.headers
            )
            
            if not response.ok:
                print(f"שגיאה בקבלת פוסטים אחרונים: {response.status_code}")
                return None

            posts_data = response.json()
            if not isinstance(posts_data, list):
                print("תגובת השרת לא בפורמט הצפוי")
                return None

            processed_posts = []
            for i, post in enumerate(posts_data):
                username = post.get('user', {}).get('username', 'משתמש לא ידוע')
                content = post.get('content', '')
                topic_title = post.get('topic', {}).get('title', 'נושא לא ידוע')
                
                soup = BeautifulSoup(content, 'html.parser')
                clean_content = soup.get_text(strip=True)
                
                # יצירת הטקסט עם הפתיח הרצוי
                post_text = f"פוסט מספר {i + 1}. פוסט מאת {username} בנושא {topic_title}. {clean_content}"
                
                # קריאה לפונקציית הניקוי בלי מספר התראה
                clean_text = clean_text_for_tts(post_text)
                
                if clean_text:
                    processed_posts.append({
                        'text': clean_text,
                        'index': i
                    })

            return processed_posts

        except Exception as e:
            print(f"שגיאה בקבלת פוסטים אחרונים: {str(e)}")
            return None
        

def get_nodebb_content(url, username, password):
    try:
        nodebb = NodeBBAPI()
        
        print(f"מנסה להתחבר עם המשתמש: {username}")
        if not nodebb.login(username, password):
            return None

        # אם זה דף התראות
        if 'notifications' in url:
            print("מבקש התראות מהשרת...")
            notifications = nodebb.get_notifications()
            if notifications and isinstance(notifications, list):
                print(f"התקבלו {len(notifications)} התראות, מעבד כל אחת בנפרד...")
                result = []
                # נוסיף מספור לכל התראה
                for i, notification in enumerate(notifications, 1):
                    # יצירת מילון עם המידע הנדרש
                    result.append({
                        'text': notification,
                        'filename': f'notification_{i:03d}'  # לדוגמה: notification_001, notification_002 וכו'
                    })
                return result
            else:
                print("לא התקבלו התראות תקינות מהשרת")
        
        return None
            
    except Exception as e:
        print(f"שגיאה בקריאת תוכן מ-NodeBB: {str(e)}")
        return None




def main():
    print("התוכנית מתחילה...")
    api = YemotAPI("0747098744", "123456")
    
    if api.login():
        print("התחברות לימות הצליחה!")
        
        # === שלוחה 1 - התראות ===
        forum_username = "ארץ הצבי"
        forum_password = "@ארץ הצבי"
        
        nodebb = NodeBBAPI()
        
        print("מנסה להתחבר לפורום...")
        if nodebb.login(forum_username, forum_password):
            print("התחברות לפורום הצליחה!")
            
            # קבלת נתוני פרופיל
            print("מושך נתוני פרופיל...")
            profile_text = nodebb.get_user_profile("ארץ הצבי")
            if profile_text:
                print("נתוני פרופיל התקבלו, מעלה ל-TTS...")
                api.upload_profile_tts(profile_text)
            else:
                print("לא התקבלו נתוני פרופיל")
                
            print("מבקש התראות מהשרת...")
            notifications = nodebb.get_notifications()
            
            if notifications and isinstance(notifications, list):
                print(f"\nהתקבלו {len(notifications)} התראות, מתחיל בהעלאה לשלוחה 1...")
                
                for index, notification in enumerate(notifications):
                    if len(notification) > 10:
                        # העלאה לשלוחה 1
                        data = {
                            "token": api.token,
                            "what": f"ivr2:/1/{index:03d}.tts",  # שלוחה 1
                            "contents": clean_text_for_tts(notification, index + 1)
                        }
                        
                        try:
                            response = requests.post(f"{api.base_url}UploadTextFile", data=data)
                            if response.status_code == 200 and response.json().get('responseStatus') == 'OK':
                                print(f"התראה {index + 1} הועלתה בהצלחה לשלוחה 1")
                            else:
                                print(f"שגיאה בהעלאת התראה {index + 1} לשלוחה 1")
                        except Exception as e:
                            print(f"שגיאה בהעלאת התראה {index + 1}: {str(e)}")
                        
                        time.sleep(2)
                
                print("\nסיום העלאת כל ההתראות לשלוחה 1")
            else:
                print("לא התקבלו התראות מהשרת")
        else:
            print("ההתחברות לפורום נכשלה")

        # === שלוחה 2 - פוסטים אחרונים ===
        print("\nמתחיל בטיפול בפוסטים אחרונים לשלוחה 2...")
        recent_posts_api = RecentPostsAPI()
        posts = recent_posts_api.get_recent_posts(limit=10)
        
        if posts:
            print(f"\nהתקבלו {len(posts)} פוסטים אחרונים, מתחיל בהעלאה לשלוחה 2...")
            
            for post in posts:
                # העלאה לשלוחה 2
                data = {
                    "token": api.token,
                    "what": f"ivr2:/2/{post['index']:03d}.tts",  # שלוחה 2
                    "contents": post['text']
                }
                
                try:
                    response = requests.post(f"{api.base_url}UploadTextFile", data=data)
                    if response.status_code == 200 and response.json().get('responseStatus') == 'OK':
                        print(f"פוסט {post['index'] + 1} הועלה בהצלחה לשלוחה 2")
                    else:
                        print(f"שגיאה בהעלאת פוסט {post['index'] + 1} לשלוחה 2")
                except Exception as e:
                    print(f"שגיאה בהעלאת פוסט {post['index'] + 1}: {str(e)}")
                
                time.sleep(2)
            
            print("\nסיום העלאת כל הפוסטים האחרונים לשלוחה 2")
        else:
            print("לא התקבלו פוסטים אחרונים")
    else:
        print("ההתחברות לימות נכשלה")
    
    print("התוכנית הסתיימה.")

if __name__ == "__main__":
    main()
