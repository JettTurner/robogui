import subprocess


class RoboCore:
    def __init__(self):
        self.process = None

    def build_command(self, cfg):
        cmd = ["robocopy", cfg["src"], cfg["dst"]]

        mode = cfg.get("mode", "copy")
        if mode == "mirror":
            cmd.append("/MIR")
        elif mode == "purge":
            cmd.append("/PURGE")
        elif mode == "move":
            cmd.append("/MOV")
        elif mode == "moveall":
            cmd.append("/MOVE")

        # subdirs — mirror and moveall imply /E
        subdirs = cfg.get("subdirs", "e")
        if mode not in ("mirror", "moveall"):
            if subdirs == "e":
                cmd.append("/E")
            elif subdirs == "s":
                cmd.append("/S")

        if cfg.get("mt"):
            cmd.append(f"/MT:{cfg['mt']}")

        if cfg.get("restartable"):
            cmd.append("/Z")

        if cfg.get("unbuffered"):
            cmd.append("/J")

        if cfg.get("tee"):
            cmd.append("/TEE")

        if cfg.get("noprogress"):
            cmd.append("/NP")

        cmd.append(f"/R:{cfg.get('retries', 2)}")
        cmd.append(f"/W:{cfg.get('wait', 1)}")

        if cfg.get("dry_run"):
            cmd.append("/L")

        return cmd

    def run(self, cmd, on_output):
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in self.process.stdout:
            on_output(line)

        return self.process.wait()

    def stop(self):
        if self.process:
            self.process.terminate()