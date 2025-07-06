#!/usr/bin/env python3
"""
하이브리드 Paper-Based Content System 서버 실행기
"""

import os
import sys
import uvicorn
import argparse
import subprocess
import signal
import time
import psutil
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime
from dotenv import load_dotenv

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로그 디렉토리 생성
log_dir = Path("./logs")
log_dir.mkdir(exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'server_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def create_directories():
    """필요한 디렉토리 생성"""
    directories = [
        "./logs",
        "./cache",
        "./cache/advanced",
        "./exports",
        "./exports/analytics",
        "./exports/monitoring",
        "./data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"디렉토리 확인/생성: {directory}")


def kill_existing_servers():
    """기존 실행 중인 서버들 종료"""
    logger.info("🔍 기존 실행 중인 서버 확인...")
    
    killed_processes = []
    
    # 특정 포트에서 실행 중인 프로세스 찾기
    ports_to_check = [8000, 8080, 3000, 3001, 3002, 3003, 3008, 5173]  # 백엔드, 프론트엔드 포트들
    
    for port in ports_to_check:
        try:
            # 포트를 사용하는 프로세스 찾기
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # 네트워크 연결 확인
                    for conn in proc.net_connections(kind='inet'):
                        if conn.laddr.port == port:
                            logger.info(f"⏹️  포트 {port}에서 실행 중인 프로세스 종료: PID {proc.pid} ({proc.name()})")
                            proc.terminate()
                            killed_processes.append((proc.pid, port, proc.name()))
                            time.sleep(1)  # 종료 대기
                            
                            # 강제 종료가 필요한 경우
                            try:
                                if proc.is_running():
                                    logger.warning(f"🔨 강제 종료: PID {proc.pid}")
                                    proc.kill()
                                    proc.wait(timeout=2)
                            except:
                                pass
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logger.debug(f"포트 {port} 확인 중 오류: {e}")
    
    # Python 프로세스 중 uvicorn, npm, node 관련 프로세스 종료
    keywords = ['uvicorn', 'npm', 'node', 'vite', 'python']
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.cmdline()).lower() if proc.cmdline() else ''
            name = proc.name().lower()
            
            # 특정 키워드가 포함된 프로세스 확인
            for keyword in keywords:
                if (keyword in cmdline or keyword in name) and \
                   ('minimal_main' in cmdline or 'app.main' in cmdline or 
                    'run_server.py' in cmdline or 'npm run dev' in cmdline or 
                    'vite' in cmdline or 'enhanced-content-system' in cmdline):
                    # 현재 프로세스와 부모 프로세스는 제외
                    if proc.pid != os.getpid() and proc.pid != os.getppid():
                        logger.info(f"⏹️  {keyword} 프로세스 종료: PID {proc.pid}")
                        proc.terminate()
                        killed_processes.append((proc.pid, keyword, proc.name()))
                        time.sleep(0.5)
                        
                        if proc.is_running():
                            proc.kill()
                        break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    if killed_processes:
        logger.info(f"✅ {len(killed_processes)}개의 기존 프로세스가 종료되었습니다.")
        for pid, info, name in killed_processes:
            logger.debug(f"   - PID {pid}: {info} ({name})")
    else:
        logger.info("✅ 종료할 기존 프로세스가 없습니다.")
    
    # 잠시 대기하여 포트가 완전히 해제되도록 함
    time.sleep(2)


def start_frontend_server():
    """프론트엔드 서버 시작"""
    frontend_path = Path(__file__).parent.parent / "frontend"
    
    if not frontend_path.exists():
        logger.warning("⚠️  프론트엔드 디렉토리를 찾을 수 없습니다.")
        return None
    
    logger.info("🚀 프론트엔드 서버 시작 중...")
    
    try:
        # package.json 확인
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            logger.warning("⚠️  package.json을 찾을 수 없습니다.")
            return None
        
        # npm run dev 실행
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,  # 새로운 프로세스 그룹 생성
            env=os.environ.copy()  # 현재 환경 변수 복사
        )
        
        # 프론트엔드 서버가 실제로 시작될 때까지 잠시 대기하고 출력 확인
        time.sleep(3)
        
        # 실행 중인 포트 찾기
        frontend_port = 3000
        for line in iter(process.stdout.readline, b''):
            if b'Local:' in line and b'http://localhost:' in line:
                try:
                    port_str = line.decode().split('http://localhost:')[1].split('/')[0]
                    frontend_port = int(port_str)
                    break
                except:
                    pass
        
        logger.info(f"✅ 프론트엔드 서버 시작됨 (PID: {process.pid})")
        logger.info(f"📱 프론트엔드: http://localhost:{frontend_port}")
        
        return process
        
    except FileNotFoundError:
        logger.error("❌ npm 명령어를 찾을 수 없습니다. Node.js가 설치되어 있는지 확인하세요.")
        return None
    except Exception as e:
        logger.error(f"❌ 프론트엔드 서버 시작 실패: {e}")
        return None


def check_environment():
    """환경 변수 확인"""
    required_vars = ["GEMINI_API_KEY"]
    missing_vars = []
    loaded_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # API 키의 일부만 표시
            if "KEY" in var or "SECRET" in var:
                masked_value = value[:10] + "..." if len(value) > 10 else value
                loaded_vars.append(f"{var}={masked_value}")
            else:
                loaded_vars.append(f"{var}={value}")
    
    if loaded_vars:
        logger.info(f"✅ 환경 변수 로드됨: {', '.join(loaded_vars)}")
    
    if missing_vars:
        logger.warning(f"⚠️  다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        logger.warning(".env 파일을 확인하거나 환경 변수를 설정해주세요.")
        
        # .env.example 파일 생성
        env_example_path = Path(".env.example")
        if not env_example_path.exists():
            with open(env_example_path, 'w') as f:
                f.write("# 환경 변수 설정 예시\n")
                f.write("GEMINI_API_KEY=your-gemini-api-key-here\n")
                f.write("DATABASE_URL=sqlite:///./data/app.db\n")
                f.write("ENVIRONMENT=development\n")
                f.write("LOG_LEVEL=INFO\n")
            logger.info(".env.example 파일이 생성되었습니다.")


def cleanup_handler(signum, frame):
    """시그널 핸들러 - 깨끗한 종료를 위해"""
    logger.info("\n⏹️  종료 신호를 받았습니다. 서버를 정리합니다...")
    sys.exit(0)

def run_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    reload: bool = True,
    workers: Optional[int] = None,
    log_level: str = "info",
    start_frontend: bool = False,
    kill_existing: bool = False
):
    """FastAPI 서버 실행"""
    frontend_process = None
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    try:
        # 기존 서버 종료 (요청된 경우)
        if kill_existing:
            kill_existing_servers()
        
        # 디렉토리 생성
        create_directories()
        
        # 환경 확인
        check_environment()
        
        # 프론트엔드 서버 시작 (요청된 경우)
        if start_frontend:
            frontend_process = start_frontend_server()
            if frontend_process:
                time.sleep(3)  # 프론트엔드 시작 대기
        
        logger.info("=" * 60)
        logger.info("🚀 Enhanced Dynamic Content System v6.1 서버 시작")
        logger.info("=" * 60)
        logger.info(f"📍 백엔드: http://{host}:{port}")
        logger.info(f"📚 API 문서: http://{host}:{port}/docs")
        logger.info(f"📖 대체 API 문서: http://{host}:{port}/redoc")
        
        if frontend_process:
            logger.info(f"📱 프론트엔드: http://localhost:3008")
        
        logger.info("=" * 60)
        
        # 개발/프로덕션 모드 설정
        if reload:
            logger.info("🔧 개발 모드로 실행 중 (자동 리로드 활성화)")
            # semaphore 경고 무시를 위한 환경 변수 설정
            env = os.environ.copy()
            env['PYTHONWARNINGS'] = 'ignore:resource_tracker'
            
            uvicorn.run(
                "app.main:app",  # 실제 구현된 main 사용
                host=host,
                port=port,
                reload=reload,
                log_level=log_level,
                reload_dirs=["./"],
                workers=1  # 단일 워커로 실행하여 multiprocessing 문제 방지
            )
        else:
            logger.info(f"🏭 프로덕션 모드로 실행 중 (워커: {workers or '자동'})")
            uvicorn.run(
                "app.main:app",
                host=host,
                port=port,
                workers=workers,
                log_level=log_level
            )
            
    except KeyboardInterrupt:
        logger.info("\n⏹️  서버가 사용자에 의해 중단되었습니다.")
        
        # 프론트엔드 프로세스 종료
        if frontend_process:
            logger.info("🔄 프론트엔드 서버 종료 중...")
            try:
                os.killpg(os.getpgid(frontend_process.pid), signal.SIGTERM)
                frontend_process.wait(timeout=5)
            except Exception as e:
                logger.debug(f"프론트엔드 정상 종료 실패: {e}")
                try:
                    frontend_process.kill()
                    frontend_process.wait(timeout=2)
                except:
                    pass
            logger.info("✅ 프론트엔드 서버 종료됨")
            
    except Exception as e:
        logger.error(f"❌ 서버 실행 중 오류 발생: {e}", exc_info=True)
        
        # 에러 발생 시 프론트엔드 프로세스 정리
        if frontend_process:
            try:
                os.killpg(os.getpgid(frontend_process.pid), signal.SIGTERM)
            except:
                frontend_process.kill()
        
        sys.exit(1)


def main():
    """메인 함수"""
    # .env 파일 로드 (로거 사용 전에 실행)
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    # 인자 먼저 파싱
    parser = argparse.ArgumentParser(
        description="Enhanced Dynamic Content System v6.1 서버",
        epilog="""
사용 예시:
  python run_server.py                     # 기존 서버 종료 후 재시작 (기본값)
  python run_server.py --no-kill           # 기존 서버 유지하고 시작
  python run_server.py --backend-only      # 백엔드만 시작
  python run_server.py --kill-only         # 기존 서버만 종료
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="서버 호스트 주소 (기본값: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="서버 포트 번호 (기본값: 8080)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        default=True,
        help="자동 리로드 활성화 (개발 모드)"
    )
    
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="자동 리로드 비활성화 (프로덕션 모드)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="워커 프로세스 수 (프로덕션 모드에서만 사용)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["critical", "error", "warning", "info", "debug"],
        default="info",
        help="로그 레벨 설정"
    )
    
    parser.add_argument(
        "--fullstack",
        action="store_true",
        default=True,
        help="프론트엔드와 백엔드를 함께 시작 (기본값: True)"
    )
    
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="백엔드만 시작 (프론트엔드 제외)"
    )
    
    parser.add_argument(
        "--no-kill",
        action="store_true",
        help="기존 서버를 종료하지 않고 시작 (기본값: 종료 후 시작)"
    )
    
    parser.add_argument(
        "--kill-only",
        action="store_true",
        help="기존 서버만 종료하고 새로 시작하지 않음"
    )
    
    args = parser.parse_args()
    
    # --kill-only 옵션 처리
    if args.kill_only:
        kill_existing_servers()
        logger.info("✅ 기존 서버 종료 완료. 새로운 서버는 시작하지 않습니다.")
        return
    
    # 기본적으로 기존 서버를 종료 (--no-kill 옵션이 없는 경우)
    if not args.no_kill:
        try:
            kill_existing_servers()
        except Exception as e:
            logger.warning(f"기존 서버 종료 중 오류 (무시하고 계속): {e}")
    
    # --no-reload 옵션 처리
    reload = not args.no_reload
    
    # 개발 모드에서는 workers 무시
    if reload and args.workers:
        logger.warning("개발 모드에서는 --workers 옵션이 무시됩니다.")
        args.workers = None
    
    # backend-only 옵션 처리
    start_frontend = args.fullstack and not args.backend_only
    
    # 서버 실행
    run_server(
        host=args.host,
        port=args.port,
        reload=reload,
        workers=args.workers,
        log_level=args.log_level,
        start_frontend=start_frontend,
        kill_existing=False  # main에서 이미 처리했으므로 여기서는 False
    )


if __name__ == "__main__":
    main()