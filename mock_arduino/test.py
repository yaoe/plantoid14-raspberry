import subprocess

def get_socat_ports():
    try:
        # Run socat and capture the standard output and standard error
        result = subprocess.run(['socat', '-d', '-d', 'pty,raw,echo=0', 'pty,raw,echo=0'], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        
        # Extract the port names from the stderr of the socat command
        lines = result.stderr.splitlines()
        if len(lines) >= 2:
            port1 = lines[0].split()[-1]
            port2 = lines[1].split()[-1]
            return port1, port2
        else:
            print("Unexpected socat output.")
            return None, None
    except subprocess.CalledProcessError:
        print("Error executing socat.")
        return None, None

if __name__ == "__main__":
    print('aaa')
    portA, portB = get_socat_ports()
    print(f"Port A: {portA}")
    print(f"Port B: {portB}")
