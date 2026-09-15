import logging
import os
import sys

import dotenv
import hydra
from loguru import logger
from omegaconf import DictConfig

from zotero_arxiv_daily.daily_research_pipeline import run_daily_file_pipeline
from zotero_arxiv_daily.utils import send_wechat_notification

os.environ["TOKENIZERS_PARALLELISM"] = "false"
dotenv.load_dotenv()


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

    output_dir = run_daily_file_pipeline(config)
    logger.info(f"Daily research file pipeline written to {output_dir}")
    digest_path = output_dir / "wechat-digest.md"
    if digest_path.exists():
        send_wechat_notification(config, digest_path.read_text(encoding="utf-8"))
    else:
        logger.warning(f"WeChat digest not found; skip notification: {digest_path}")


if __name__ == "__main__":
    main()
