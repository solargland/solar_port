import os
import sys
import time
import argparse
import subprocess
import datetime
from main import run_pipeline

def register_windows_tasks(morning_time: str = "08:00", evening_time: str = "20:00", send_email: bool = True):
    """
    为 Windows 注册早报与晚报两个系统级静默定时任务
    """
    python_exe = sys.executable
    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_dir, "main.py")

    tasks = [
        ("SolarPort_Morning", morning_time, "早报"),
        ("SolarPort_Evening", evening_time, "晚报"),
    ]

    print(f"[*] 正在为 Windows 注册【早报】与【晚报】系统计划任务...")

    for task_name, t_time, edition in tasks:
        cmd_args = f'"{python_exe}" "{main_script}" --edition {edition}'
        if send_email:
            cmd_args += " --send-email"

        schtasks_cmd = [
            "schtasks", "/Create",
            "/SC", "DAILY",
            "/TN", task_name,
            "/TR", cmd_args,
            "/ST", t_time,
            "/F"
        ]

        print(f"\n[*] 注册【{edition}】任务: {task_name} (每天 {t_time})")
        try:
            res = subprocess.run(schtasks_cmd, capture_output=True, text=True, check=True)
            print(f"[+] 【{edition}】任务注册成功！")
        except subprocess.CalledProcessError as e:
            print(f"[-] 注册【{edition}】任务失败: {e.stderr.strip()}")
            print("💡 提示: 若权限不足，请右键选择'以管理员身份运行'终端。")

    print("\n💡 您可以在 Windows '任务计划程序' 中随时查看或手动触发这两个任务。")

def unregister_windows_tasks():
    """注销早报与晚报 Windows 计划任务"""
    for task_name in ["SolarPort_Morning", "SolarPort_Evening", "GlobalDailyNewsCrawler"]:
        schtasks_cmd = ["schtasks", "/Delete", "/TN", task_name, "/F"]
        try:
            subprocess.run(schtasks_cmd, capture_output=True, text=True, check=True)
            print(f"[+] 计划任务 [{task_name}] 已删除。")
        except subprocess.CalledProcessError:
            pass

def run_loop_scheduler(morning_time: str = "08:00", evening_time: str = "20:00", send_email: bool = True):
    """常驻后台循环调度器（早报 08:00 + 晚报 20:00）"""
    print(f"[*] 启动早晚报后台调度服务:")
    print(f"    - 早报触发时间: {morning_time}")
    print(f"    - 晚报触发时间: {evening_time}")
    print("[*] 保持该终端运行，按 Ctrl+C 可停止。\n")

    m_h, m_m = map(int, morning_time.split(":"))
    e_h, e_m = map(int, evening_time.split(":"))

    last_morning_run = None
    last_evening_run = None

    while True:
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")

        # 检查早报
        if now.hour == m_h and now.minute >= m_m and last_morning_run != current_date:
            print(f"\n[+] 触发每日【早报】任务: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            try:
                run_pipeline(limit=5, send_email=send_email, edition="早报")
                last_morning_run = current_date
            except Exception as e:
                print(f"[-] 早报任务执行异常: {e}")

        # 检查晚报
        if now.hour == e_h and now.minute >= e_m and last_evening_run != current_date:
            print(f"\n[+] 触发每日【晚报】任务: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            try:
                run_pipeline(limit=5, send_email=send_email, edition="晚报")
                last_evening_run = current_date
            except Exception as e:
                print(f"[-] 晚报任务执行异常: {e}")

        time.sleep(30)

def main():
    parser = argparse.ArgumentParser(description="全球社交媒体早报晚报定时调度器")
    parser.add_argument("--morning-time", type=str, default="08:00", help="早报触发时间 (默认 08:00)")
    parser.add_argument("--evening-time", type=str, default="20:00", help="晚报触发时间 (默认 20:00)")
    parser.add_argument("--no-email", action="store_true", help="不发送邮件")
    parser.add_argument("--register-windows-task", action="store_true", help="一键注册早报与晚报为 Windows 系统定时任务")
    parser.add_argument("--unregister-windows-task", action="store_true", help="删除 Windows 定时任务")
    parser.add_argument("--run-now", action="store_true", help="立即执行一次抓取与推送")
    parser.add_argument("--edition", type=str, default="auto", choices=["auto", "早报", "晚报"], help="立即执行时的期号")

    args = parser.parse_args()
    send_email = not args.no_email

    if args.register_windows_task:
        register_windows_tasks(morning_time=args.morning_time, evening_time=args.evening_time, send_email=send_email)
    elif args.unregister_windows_task:
        unregister_windows_tasks()
    elif args.run_now:
        run_pipeline(limit=5, send_email=send_email, edition=args.edition)
    else:
        run_loop_scheduler(morning_time=args.morning_time, evening_time=args.evening_time, send_email=send_email)

if __name__ == "__main__":
    main()
