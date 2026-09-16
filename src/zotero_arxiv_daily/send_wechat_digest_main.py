import logging
import os
import sys
from pathlib import Path

import dotenv
import hydra
from loguru import logger
from omegaconf import DictConfig

from zotero_arxiv_daily.utils import send_wechat_notification

os.environ["TOKENIZERS_PARALLELISM"] = "false"
dotenv.load_dotenv()


def _latest_daily_output(root: Path) -> Path:
    candidates = sorted(path for path in root.iterdir() if path.is_dir())
    if not candidates:
        raise RuntimeError(f"No daily output folders found under {root}")
    return candidates[-1]


@hydra.main(version_base=None, config_path="../../config", config_name="default")
def main(config: DictConfig):
    log_level = "DEBUG" if config.executor.debug else "INFO"
    logger.remove()
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    for logger_name in logging.root.manager.loggerDict:
        if "zotero_arxiv_daily" in logger_name:
            continue
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    output_root = Path(os.getenv("DAILY_PIPELINE_OUTPUT_ROOT", "outputs/daily"))
    output_dir = _latest_daily_output(output_root)
    digest_path = output_dir / "wechat-digest.md"
    if not digest_path.exists():
        raise RuntimeError(f"WeChat digest not found; cannot send notification: {digest_path}")
    send_wechat_notification(config, digest_path.read_text(encoding="utf-8"))
    logger.info(f"WeChat digest sent from {digest_path}")


if __name__ == "__main__":
    main()
