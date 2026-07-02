import fitz, os
files = [
  r"F:\My Drive\01 project\ai\bma-plan\20250616_RAMA4 APARTMENT PERMIT rev 1.pdf",
  r"F:\My Drive\01 project\ai\bma-plan\sandbox\251121_CHH_Submission_REV2 - Copy.pdf",
]
for f in files:
    name = os.path.basename(f)
    sz = os.path.getsize(f)/1e6
    # method 1: fitz fast webaccess
    try:
        doc = fitz.open(f)
        fast = doc.is_fast_webaccess
        npages = doc.page_count
        doc.close()
    except Exception as e:
        fast = f"ERR {e}"; npages="?"
    # method 2: scan first 2KB for /Linearized
    with open(f,'rb') as fh:
        head = fh.read(2048)
    lin_token = b'/Linearized' in head
    print(f"{name}")
    print(f"  size={sz:.1f}MB pages={npages}")
    print(f"  fitz.is_fast_webaccess={fast}")
    print(f"  /Linearized in first 2KB={lin_token}")
