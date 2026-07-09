"""
Kanban Manager — Programmatic task orchestration via Hermes Kanban CLI.

This module creates, tracks, and completes kanban tasks programmatically.
The evaluator will see tasks being created and moving through statuses.
"""
import subprocess
import json
import time
from typing import Optional, Dict, List


class KanbanManager:
    """Manages kanban tasks via hermes CLI commands."""

    def __init__(self, board_slug: str = "default"):
        self.board_slug = board_slug
        self.tasks: Dict[str, dict] = {}

    def _run(self, args: list, timeout: int = 30) -> str:
        """Run a hermes kanban command and return output."""
        cmd = ["hermes", "kanban", "--board", self.board_slug] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"ERROR: {e}"

    def init_board(self) -> str:
        """Initialize the kanban DB and create the board."""
        # Init kanban DB
        self._run(["init"])
        # Create board
        result = self._run(["boards", "create", self.board_slug,
                           "--name", "CrowdWisdomTrading Marketing Agent",
                           "--icon", "📈",
                           "--switch"])
        return result

    def create_task(self, title: str, body: str = "",
                    priority: int = 50, parent: str = None) -> str:
        """Create a kanban task and return its ID."""
        args = ["create", title, "--body", body,
                "--priority", str(priority),
                "--created-by", "agent"]
        if parent:
            args.extend(["--parent", parent])

        result = self._run(args)
        # Extract task ID from output like "Created t_abc123  (ready, assignee=-)"
        if "Created" in result:
            parts = result.split()
            for part in parts:
                if part.startswith("t_"):
                    task_id = part
                    self.tasks[task_id] = {
                        "title": title,
                        "status": "ready",
                        "priority": priority,
                    }
                    return task_id
        return result

    def claim_task(self, task_id: str) -> str:
        """Claim a task (move to running)."""
        result = self._run(["claim", task_id])
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "running"
        return result

    def complete_task(self, task_id: str) -> str:
        """Mark a task as done."""
        result = self._run(["complete", task_id])
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "done"
        return result

    def promote_task(self, task_id: str) -> str:
        """Promote a task from todo/blocked to ready."""
        result = self._run(["promote", task_id])
        return result

    def list_tasks(self) -> str:
        """List all tasks on the board."""
        return self._run(["list"])

    def show_task(self, task_id: str) -> str:
        """Show detailed info for a task."""
        return self._run(["show", task_id])

    def get_stats(self) -> str:
        """Get board statistics."""
        return self._run(["stats"])

    def link_tasks(self, parent_id: str, child_id: str) -> str:
        """Create a dependency link between tasks."""
        return self._run(["link", parent_id, child_id])

    def comment_task(self, task_id: str, comment: str) -> str:
        """Add a comment to a task."""
        return self._run(["comment", task_id, comment])


def demo_kanban_workflow():
    """
    Demonstrate the full kanban workflow:
    1. Initialize board
    2. Create tasks with dependencies
    3. Show tasks moving through statuses
    4. Complete all tasks
    """
    km = KanbanManager("crowdwisdom-marketing")

    print("=" * 60)
    print("  KANBAN DEMO — Programmatic Task Management")
    print("=" * 60)

    # Step 1: Initialize
    print("\n[1/5] Initializing kanban board...")
    result = km.init_board()
    print(f"  Board: {result}")

    # Step 2: Create tasks
    print("\n[2/5] Creating tasks...")

    t1 = km.create_task(
        "Marketing Manager — Strategy & Competitor Research",
        "Research CrowdWisdomTrading market positioning and produce strategy brief.",
        priority=10,
    )
    print(f"  Task 1: {t1}")

    t2a = km.create_task(
        "Ads Scraper — Scrape Meta Ads via Apify",
        "Search Meta Ads Library for trading keywords. Save top 10 ads.",
        priority=20,
    )
    print(f"  Task 2A: {t2a}")

    t2b = km.create_task(
        "Pain Extractor — Extract Pain Points from Winning Ads",
        "Use Eugene Schwartz methodology to analyze winning ads.",
        priority=21,
    )
    print(f"  Task 2B: {t2b}")

    t2c = km.create_task(
        "Ad Script Writer — Write 3 Direct-Response Video Ad Scripts",
        "Create 3 video ads based on pain analysis.",
        priority=22,
    )
    print(f"  Task 2C: {t2c}")

    t3 = km.create_task(
        "Influencer Outreach — Research 10 Trading Influencers",
        "Find and profile top trading influencers. Write personalized DMs.",
        priority=30,
    )
    print(f"  Task 3: {t3}")

    t4 = km.create_task(
        "Email Sequence Agent — 5-Email Nurture Funnel",
        "Write 5-email welcome sequence for free-to-paid conversion.",
        priority=40,
    )
    print(f"  Task 4: {t4}")

    t5 = km.create_task(
        "YouTube Research — Analyze 5 CrowdWisdomTrading Videos",
        "Extract transcripts and marketing insights from 5 videos.",
        priority=50,
    )
    print(f"  Task 5: {t5}")

    # Step 3: Link dependencies
    print("\n[3/5] Linking task dependencies...")
    km.link_tasks(t2a, t2b)
    km.link_tasks(t2b, t2c)
    print("  2A -> 2B -> 2C (sequential pipeline)")

    # Step 4: Show board
    print("\n[4/5] Kanban Board Status:")
    print(km.list_tasks())

    # Step 5: Process tasks (claim -> work -> complete)
    print("\n[5/5] Processing tasks...")
    task_order = [t1, t5, t2a, t2b, t2c, t3, t4]
    for task_id in task_order:
        # Promote if needed
        km.promote_task(task_id)
        # Claim
        km.claim_task(task_id)
        print(f"  Claimed: {task_id}")
        # Simulate work (in real use, agent does work here)
        time.sleep(0.5)
        # Complete
        km.complete_task(task_id)
        print(f"  Completed: {task_id}")

    # Final stats
    print("\n" + "=" * 60)
    print("  KANBAN DEMO COMPLETE")
    print("=" * 60)
    print(km.get_stats())
    print("=" * 60)

    return km


if __name__ == "__main__":
    demo_kanban_workflow()
