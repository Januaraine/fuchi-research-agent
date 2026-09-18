"""ingestion CLI：`python -m app.ingest --titles "..." "..."`。

示例：
    python -m app.ingest --titles "Transformer (deep learning)" "BERT (language model)"
"""
from __future__ import annotations

import argparse

from ..database import Base, SessionLocal, engine
from .pipeline import run_wikipedia_ingestion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Knowledge Observatory 数据接入 pipeline")
    parser.add_argument("--source", choices=["wikipedia"], default="wikipedia")
    parser.add_argument(
        "--titles",
        nargs="+",
        required=True,
        help="Wikipedia 页面标题（含空格的标题用引号包裹）",
    )
    parser.add_argument(
        "--max-relations",
        type=int,
        default=20,
        help="每个页面最多建立的 related_to 关系数（默认 20）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        result = run_wikipedia_ingestion(db, args.titles, max_relations=args.max_relations)
    print(f"[run #{result['run_id']}] {result['status']} "
          f"fetched={result['fetched']} inserted={result['inserted']} "
          f"updated={result['updated']} skipped={result['skipped']} "
          f"relations={result['relations_created']}")
    if result["message"]:
        print(result["message"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
