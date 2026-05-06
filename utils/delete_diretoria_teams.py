import csv
import requests
import time

# Dados do model curl do usuário
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJhdWQiOiJodHRwczpcL1wvY2l0eS5mYWNpbGl0YXZlbmRhcy5jb20iLCJnb3Njb3JlLXRva2VuLXVzZXIiOiJleUpwZGlJNklsYzNaMlZHUTBveGRIQjVXWGhrWlVwdVVWbDFkVUU5UFNJc0luWmhiSFZsSWpvaWFIUllPR2hPWWt4Uk1HNTJVbkE1ZWpjMFoyOVFUMWhQYXpOSVEyeGxhbFZZYzNGUWFYWnhUWEpvVGxGblpubExWMVZFWVU1c2RWSnljR1JMY2pWNmFsRTNlR2c0YTFWTWVVSlZUVFpFY0ZSRVhDOVVVbUZSUFQwaUxDSnRZV01pT2lJNVlXTTBZalE0TldSaU16bGtNamN5TTJVeE9XTXdPRFl3WmpnM1lqRTBaR015TVRJMVlUUmlOalppTVRJd05UYzVZVGt5Wm1ZMlkyUmhaREk1T1RReUluMD0iLCJzdWIiOjUxNywiaXNzIjoiaHR0cHM6XC9cL2NpdHkuYXBpLmZhY2lsaXRhdmVuZGFzLmNvbVwvYXBpXC92MVwvYXV0aGVudGljYXRlIiwiaWF0IjoiMTc3NjE5ODY0NiIsImV4cCI6IjE3ODEzODI2NDYiLCJuYmYiOiIxNzc2MTk4NjQ2IiwianRpIjoiZjBiZTMzNDg0MjkwNmRkYmYxNjUwODI1MjljYjVhOTIifQ.YmI4NDA2YWVjODk1ODAwMTNmNzg4NDQ5OWZhZjNmYWI4ZDM1NjU5ZTU3NDI3NmI1MmY0NWMwZmU3N2EzY2I1MA',
    'cache-control': 'no-cache',
    'dnt': '1',
    'goscore-token': '518c2b22e9372a2e8bd0cda98b14e21d',
    'origin': 'https://city.facilitavendas.com',
    'pragma': 'no-cache',
    'referer': 'https://city.facilitavendas.com/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
}

COOKIES_STR = '_hjSessionUser_2354284=eyJpZCI6IjAxYzZjOWFjLTM2OTAtNTg4Mi04NjU4LTc5ODAzODBhMzcyYSIsImNyZWF0ZWQiOjE3NzQwMTYzNzU2ODYsImV4aXN0aW5nIjp0cnVlfQ==; cartalyst_sentry=eyJpdiI6InJSR0VYQzczT0c3THVEMUY0TlNmUXc9PSIsInZhbHVlIjoiNE0xSHB1bVwvODMrQ2xmajVYemtKdENNZlB3aXFjNEo5MTlxRWNyXC9qNWhyc2lWc3JiOThcLzdkMTNjbG9uYUh3UGF5c09HYjloU0FkY3VmM2NGOUZwaFJzMWdDRUk4UVd4cVF2eFwvTFBMQWR4bGVaMVBxdUNsbnZETFppNjRCeHJFIiwibWFjIjoiZGU5MWMwY2YxMmY2YmM5NjczOGZkZDBmNmU1YjEyOTViODdmMTAwZTkxNDY3ZWE2MGE1NzA5ZTQ0ZDQzN2RkMyJ9; PHPSESSID=ppfm57gpt4knrkt3b098ibl4c5; _gid=GA1.2.868643631.1776883263; _ga=GA1.1.73717036.1772114248; _clck=t73ne7%5E2%5Eg5g%5E0%5E2248; _hjSession_2354284=eyJpZCI6ImI5ZWU3ZGNiLTVlMjQtNDJkYy05NTY1LWQzM2Y1ZjM5YmI5YSIsImMiOjE3NzY5NTYxNDkwMzgsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowfQ==; _clsk=plb9sc%5E1776956172186%5E5%5E1%5Ea.clarity.ms%2Fcollect; laravel_session=eyJpdiI6ImdUYnlESkJGWWF5a0YxQzNOdCsxdWc9PSIsInZhbHVlIjoiSnVpUVFQSlp3VjM4ZU01R0F2M0o3U0crSndHdkxiZmpmUjB3TFNGUTZRMGVmb3FFMkNoa3FwOVdLRlhOamdndzhmTmFOR3VaSG1hUDZ3VkE2eTNNSUE9PSIsIm1hYyI6IjZjZDExMzZiM2RjZDFlZWQ4MWVkZDc5N2ZlNDY3YTgzNWQ3ZWI3NjQwNWRiOWQ5ZTNlOWNjYzBkNjViZTFiMTUifQ%3D%3D; _ga_4Y48ZYP9EX=GS2.1.s1776956148$o21$g1$t1776956291$j60$l0$h0; _ga_P4WF2YCTNX=GS2.1.s1776956149$o20$g1$t1776956291$j60$l0$h0'

COOKIES = {c.split('=')[0].strip(): '='.join(c.split('=')[1:]).strip() for c in COOKIES_STR.split(';') if '=' in c}

def delete_team(team_id, team_name):
    url = f"https://city.api.facilitavendas.com/api/v1/teams/{team_id}/11"
    print(f"Deleting team {team_id} ({team_name})...", end=' ', flush=True)
    try:
        response = requests.delete(url, headers=HEADERS, cookies=COOKIES, timeout=30)
        if response.status_code == 200:
            print("OK", flush=True)
            return True
        else:
            print(f"FAIL (Status {response.status_code}: {response.text})", flush=True)
            return False
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        return False

def main():
    teams_to_delete = []
    with open('csv/imob.csv', mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('GerenteCV') == 'DIRETORIA' and row.get('team_id'):
                teams_to_delete.append((row['team_id'], row['Imobiliaria']))
    
    print(f"Found {len(teams_to_delete)} teams to process.", flush=True)
    
    success_count = 0
    fail_count = 0
    
    for team_id, team_name in teams_to_delete:
        if delete_team(team_id, team_name):
            success_count += 1
        else:
            fail_count += 1
        time.sleep(0.3) # Amigável para o servidor
    
    print(f"\nFinalizado!", flush=True)
    print(f"Sucessos: {success_count}", flush=True)
    print(f"Falhas: {fail_count}", flush=True)

if __name__ == "__main__":
    main()
