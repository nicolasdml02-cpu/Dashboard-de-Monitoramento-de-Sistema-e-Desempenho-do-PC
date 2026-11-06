import psutil
import time

_ultima_leitura_rede = None
_ultimo_tempo_rede = None

def obter_metricas_gerais():
    global _ultima_leitura_rede, _ultimo_tempo_rede

    cpu_uso = psutil.cpu_percent(interval=0.1)
    
    memoria = psutil.virtual_memory()
    ram_uso = memoria.percent
    ram_total_gb = round(memoria.total / (1024 ** 3), 2)
    ram_usada_gb = round(memoria.used / (1024 ** 3), 2)
    
    disco = psutil.disk_usage('/')
    disco_uso = disco.percent
    disco_total_gb = round(disco.total / (1024 ** 3), 2)
    disco_usado_gb = round(disco.used / (1024 ** 3), 2)
    
    contador_rede = psutil.net_io_counters()
    tempo_atual = time.time()
    
    download_kbps = 0.0
    upload_kbps = 0.0
    
    if _ultima_leitura_rede is not None and _ultimo_tempo_rede is not None:
        intervalo_tempo = tempo_atual - _ultimo_tempo_rede
        if intervalo_tempo > 0:
            bytes_baixados = contador_rede.bytes_recv - _ultima_leitura_rede.bytes_recv
            bytes_enviados = contador_rede.bytes_sent - _ultima_leitura_rede.bytes_sent
            
            download_kbps = round((bytes_baixados / 1024) / intervalo_tempo, 2)
            upload_kbps = round((bytes_enviados / 1024) / intervalo_tempo, 2)
            
    _ultima_leitura_rede = contador_rede
    _ultimo_tempo_rede = tempo_atual

    return {
        "cpu": cpu_uso,
        "ram_percent": ram_uso,
        "ram_total": ram_total_gb,
        "ram_usada": ram_usada_gb,
        "disco_percent": disco_uso,
        "disco_total": disco_total_gb,
        "disco_usado": disco_usado_gb,
        "rede_down": download_kbps,
        "rede_up": upload_kbps
    }

def listar_processos_ativos():
    processos = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            pinfo['cpu_percent'] = pinfo['cpu_percent'] or 0.0
            pinfo['memory_percent'] = round(pinfo['memory_percent'] or 0.0, 2)
            processos.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    processos = sorted(processos, key=lambda p: p['cpu_percent'], reverse=True)
    return processos[:50]

def finalizar_processo(pid):
    """Encerra um processo com segurança com base no seu PID."""
    try:
        p = psutil.Process(pid)
        p.terminate() # Encerramento suave
        return True
    except Exception as e:
        print(f"Erro ao finalizar processo {pid}: {e}")
        return False