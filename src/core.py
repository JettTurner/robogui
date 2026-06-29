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

        subdirs = cfg.get("subdirs", "e")
        if mode not in ("mirror", "moveall"):
            if subdirs == "e":
                cmd.append("/E")
            elif subdirs == "s":
                cmd.append("/S")

        # ---- Copy Options ----

        if cfg.get("zb"):
            cmd.append("/ZB")
        elif cfg.get("z"):
            cmd.append("/Z")
        if cfg.get("b") and not cfg.get("zb"):
            cmd.append("/B")

        if cfg.get("j"):
            cmd.append("/J")

        if cfg.get("efsraw"):
            cmd.append("/EFSRAW")

        lev = cfg.get("lev", 0)
        if lev > 0:
            cmd.append(f"/LEV:{lev}")

        copy_flags = cfg.get("copy_flags", "").strip()
        if copy_flags:
            cmd.append(f"/COPY:{copy_flags}")

        dcopy_flags = cfg.get("dcopy_flags", "").strip()
        if dcopy_flags:
            cmd.append(f"/DCOPY:{dcopy_flags}")

        if cfg.get("sec"):
            cmd.append("/SEC")
        if cfg.get("copyall"):
            cmd.append("/COPYALL")
        if cfg.get("nocopy"):
            cmd.append("/NOCOPY")
        if cfg.get("secfix"):
            cmd.append("/SECFIX")
        if cfg.get("timfix"):
            cmd.append("/TIMFIX")

        add_attr = cfg.get("add_attr", "").strip()
        if add_attr:
            cmd.append(f"/A+:{add_attr}")
        remove_attr = cfg.get("remove_attr", "").strip()
        if remove_attr:
            cmd.append(f"/A-:{remove_attr}")

        if cfg.get("create"):
            cmd.append("/CREATE")
        if cfg.get("fat"):
            cmd.append("/FAT")
        if cfg.get("no256"):
            cmd.append("/256")
        if cfg.get("sj"):
            cmd.append("/SJ")
        if cfg.get("sl"):
            cmd.append("/SL")

        if cfg.get("nodcopy"):
            cmd.append("/NODCOPY")
        if cfg.get("nooffload"):
            cmd.append("/NOOFFLOAD")
        if cfg.get("compress"):
            cmd.append("/COMPRESS")

        sparse = cfg.get("sparse", "")
        if sparse:
            cmd.append(f"/SPARSE:{sparse}")

        if cfg.get("noclone"):
            cmd.append("/NOCLONE")

        mon = cfg.get("mon", 0)
        if mon > 0:
            cmd.append(f"/MON:{mon}")
        mot = cfg.get("mot", 0)
        if mot > 0:
            cmd.append(f"/MOT:{mot}")

        rh = cfg.get("rh", "").strip()
        if rh:
            cmd.append(f"/RH:{rh}")
        if cfg.get("pf"):
            cmd.append("/PF")

        ipg = cfg.get("ipg", 0)
        if ipg > 0:
            cmd.append(f"/IPG:{ipg}")

        # ---- File Throttling ----

        iomaxsize = cfg.get("iomaxsize", "").strip()
        if iomaxsize:
            cmd.append(f"/IOMAXSIZE:{iomaxsize}")
        iorate = cfg.get("iorate", "").strip()
        if iorate:
            cmd.append(f"/IORATE:{iorate}")
        threshold = cfg.get("threshold", "").strip()
        if threshold:
            cmd.append(f"/THRESHOLD:{threshold}")

        # ---- File Selection ----

        if cfg.get("archive_a"):
            cmd.append("/A")
        if cfg.get("archive_m"):
            cmd.append("/M")

        include_attr = cfg.get("include_attr", "").strip()
        if include_attr:
            cmd.append(f"/IA:{include_attr}")
        exclude_attr = cfg.get("exclude_attr", "").strip()
        if exclude_attr:
            cmd.append(f"/XA:{exclude_attr}")

        exclude_files = cfg.get("exclude_files", "").strip()
        if exclude_files:
            for f in exclude_files.split():
                cmd.append(f"/XF:{f}")
        exclude_dirs = cfg.get("exclude_dirs", "").strip()
        if exclude_dirs:
            for d in exclude_dirs.split():
                cmd.append(f"/XD:{d}")

        if cfg.get("xc"):
            cmd.append("/XC")
        if cfg.get("xn"):
            cmd.append("/XN")
        if cfg.get("xo"):
            cmd.append("/XO")
        if cfg.get("xx"):
            cmd.append("/XX")
        if cfg.get("xl"):
            cmd.append("/XL")
        if cfg.get("im"):
            cmd.append("/IM")
        if cfg.get("is_same"):
            cmd.append("/IS")
        if cfg.get("it"):
            cmd.append("/IT")

        max_size = cfg.get("max_size", 0)
        if max_size > 0:
            cmd.append(f"/MAX:{max_size}")
        min_size = cfg.get("min_size", 0)
        if min_size > 0:
            cmd.append(f"/MIN:{min_size}")
        max_age = cfg.get("max_age", 0)
        if max_age > 0:
            cmd.append(f"/MAXAGE:{max_age}")
        min_age = cfg.get("min_age", 0)
        if min_age > 0:
            cmd.append(f"/MINAGE:{min_age}")
        max_lad = cfg.get("max_lad", 0)
        if max_lad > 0:
            cmd.append(f"/MAXLAD:{max_lad}")
        min_lad = cfg.get("min_lad", 0)
        if min_lad > 0:
            cmd.append(f"/MINLAD:{min_lad}")

        if cfg.get("xj"):
            cmd.append("/XJ")
        if cfg.get("fft"):
            cmd.append("/FFT")
        if cfg.get("dst_comp"):
            cmd.append("/DST")
        if cfg.get("xjd"):
            cmd.append("/XJD")
        if cfg.get("xjf"):
            cmd.append("/XJF")

        # ---- Retry Options ----

        cmd.append(f"/R:{cfg.get('retries', 2)}")
        cmd.append(f"/W:{cfg.get('wait', 1)}")

        if cfg.get("reg"):
            cmd.append("/REG")
        if cfg.get("tbd"):
            cmd.append("/TBD")

        if cfg.get("lfsm"):
            lfsm_size = cfg.get("lfsm_size", "").strip()
            if lfsm_size:
                cmd.append(f"/LFSM:{lfsm_size}")
            else:
                cmd.append("/LFSM")

        # ---- Logging Options ----

        if cfg.get("dry_run") or cfg.get("list_only"):
            cmd.append("/L")

        if cfg.get("x_report"):
            cmd.append("/X")
        if cfg.get("v"):
            cmd.append("/V")
        if cfg.get("ts"):
            cmd.append("/TS")
        if cfg.get("fp"):
            cmd.append("/FP")
        if cfg.get("bytes"):
            cmd.append("/BYTES")
        if cfg.get("ns"):
            cmd.append("/NS")
        if cfg.get("nc"):
            cmd.append("/NC")
        if cfg.get("nfl"):
            cmd.append("/NFL")
        if cfg.get("ndl"):
            cmd.append("/NDL")
        if cfg.get("eta"):
            cmd.append("/ETA")
        if cfg.get("njh"):
            cmd.append("/NJH")
        if cfg.get("njs"):
            cmd.append("/NJS")
        if cfg.get("unicode"):
            cmd.append("/UNICODE")
        if cfg.get("log_tee"):
            cmd.append("/TEE")

        log_file = cfg.get("log_file", "").strip()
        if log_file:
            cmd.append(f"/LOG:{log_file}")
        log_append_file = cfg.get("log_append_file", "").strip()
        if log_append_file:
            cmd.append(f"/LOG+:{log_append_file}")
        unilog_file = cfg.get("unilog_file", "").strip()
        if unilog_file:
            cmd.append(f"/UNILOG:{unilog_file}")
        unilog_append_file = cfg.get("unilog_append_file", "").strip()
        if unilog_append_file:
            cmd.append(f"/UNILOG+:{unilog_append_file}")

        # ---- Job Options ----

        job_name = cfg.get("job_name", "").strip()
        if job_name:
            cmd.append(f"/JOB:{job_name}")
        save_name = cfg.get("save_name", "").strip()
        if save_name:
            cmd.append(f"/SAVE:{save_name}")

        if cfg.get("quit"):
            cmd.append("/QUIT")
        if cfg.get("nosd"):
            cmd.append("/NOSD")
        if cfg.get("nodd"):
            cmd.append("/NODD")

        if_files = cfg.get("if_files", "").strip()
        if if_files:
            for f in if_files.split():
                cmd.append(f"/IF:{f}")

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
