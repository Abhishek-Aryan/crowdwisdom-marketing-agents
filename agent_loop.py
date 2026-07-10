"""
Agent Loop — Goal-directed agent execution with skill loading.

This module implements the agent loop pattern:
1. Load relevant skills
2. Set a goal
3. Loop: agent thinks -> acts -> observes -> repeats until goal achieved
4. Save output to Obsidian vault
"""
import os
import sys
import json
import datetime
from typing import Optional, Callable

# Import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    MODEL, OBSIDIAN_VAULT, OUTPUT_DIR,
    load_product_context, SKILLS_DIR,
)

# Import Hermes AIAgent
try:
    from run_agent import AIAgent
except ImportError:
    # Fallback: add hermes source to path
    HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    HERMES_SRC = os.path.join(HERMES_HOME, "hermes-agent")
    if os.path.isdir(HERMES_SRC):
        sys.path.insert(0, HERMES_SRC)
    from run_agent import AIAgent


class AgentLoop:
    """
    Goal-directed agent with skill loading and iterative refinement.

    The agent loop:
    1. Loads relevant skills from the skills directory
    2. Constructs a system prompt with product context + skills
    3. Runs the agent with a goal
    4. If the agent's response needs refinement, loops with feedback
    5. Saves the final output to Obsidian vault
    """

    def __init__(self, name: str, role: str, system_prompt: str,
                 skills: list = None, max_iterations: int = 3):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.skills = skills or []
        self.max_iterations = max_iterations
        self.iteration = 0
        self.history = []

    def _load_skills(self) -> str:
        """Load skill files from the skills directory."""
        skill_content = []
        for skill_name in self.skills:
            skill_path = os.path.join(SKILLS_DIR, f"{skill_name}.md")
            if os.path.exists(skill_path):
                with open(skill_path, "r", encoding="utf-8") as f:
                    skill_content.append(f"### Skill: {skill_name}\n{f.read()}")
        return "\n\n".join(skill_content) if skill_content else ""

    def _build_system_prompt(self) -> str:
        """Build the full system prompt with context and skills."""
        product_context = load_product_context()
        skills_content = self._load_skills()

        parts = [self.system_prompt]

        if product_context:
            parts.append(f"\n\n## Product Context\n{product_context}")

        if skills_content:
            parts.append(f"\n\n## Loaded Skills\n{skills_content}")

        return "\n".join(parts)

    def _create_agent(self) -> AIAgent:
        """Create an isolated Hermes agent."""
        full_prompt = self._build_system_prompt()
        return AIAgent(
            model=MODEL,
            ephemeral_system_prompt=full_prompt,
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            platform="cli",
        )

    def run(self, goal: str, save_as: str = None,
            on_progress: Callable = None) -> str:
        """
        Run the agent loop to achieve a goal.

        Args:
            goal: What the agent should accomplish
            save_as: Filename to save output in Obsidian vault
            on_progress: Optional callback for progress updates

        Returns:
            The agent's final output
        """
        print(f"\n{'='*60}")
        print(f"  AGENT: {self.name} ({self.role})")
        print(f"  GOAL: {goal[:80]}...")
        print(f"  SKILLS: {', '.join(self.skills) if self.skills else 'none'}")
        print(f"  MAX ITERATIONS: {self.max_iterations}")
        print(f"{'='*60}")

        agent = self._create_agent()
        current_goal = goal
        best_result = ""

        for iteration in range(1, self.max_iterations + 1):
            self.iteration = iteration
            print(f"\n  [Iteration {iteration}/{self.max_iterations}]")

            if on_progress:
                on_progress(self.name, iteration, "thinking")

            # Run the agent
            result = agent.chat(current_goal)
            self.history.append({
                "iteration": iteration,
                "goal": current_goal,
                "result": result,
                "timestamp": datetime.datetime.now().isoformat(),
            })

            print(f"  Response: {len(result)} chars")

            if on_progress:
                on_progress(self.name, iteration, "complete")

            # Quality check: must be substantial AND contain markdown structure
            has_length = len(result) > 500
            has_structure = any(marker in result for marker in ["##", "**", "- ", "1.", "\n\n"])
            is_quality = has_length and has_structure

            if is_quality:
                best_result = result
                print(f"  ✓ Result accepted (iteration {iteration}, {len(result)} chars)")
                break
            else:
                reason = []
                if not has_length:
                    reason.append(f"too short ({len(result)} chars, need 500+)")
                if not has_structure:
                    reason.append("no markdown structure (##, **, lists)")
                feedback = ", ".join(reason)
                current_goal = f"{goal}\n\nYour previous response needs improvement: {feedback}. Please provide a more detailed, well-structured Markdown response with headers (##), bullet points, and specific actionable content."
                best_result = result
                print(f"  → Refining: {feedback}")

        # Save to Obsidian vault if filename provided
        if save_as:
            self._save_output(save_as, best_result)

        return best_result

    def _save_output(self, filename: str, content: str):
        """Save output to Obsidian vault."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        md_content = f"# {self.name}\n*Generated: {timestamp}*\n*Agent: {self.name} ({self.role})*\n*Iterations: {self.iteration}*\n\n{content}"

        # Save to Obsidian vault
        vault_path = os.path.join(OBSIDIAN_VAULT, filename)
        with open(vault_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  [Obsidian] Saved → {vault_path}")

        # Also save to local output
        local_path = os.path.join(OUTPUT_DIR, filename)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"  [Local] Saved → {local_path}")


def create_marketing_agent() -> AgentLoop:
    """Create the Marketing Manager agent."""
    return AgentLoop(
        name="Marketing Manager",
        role="Strategy & Competitor Research",
        system_prompt="""You are a senior marketing strategist for CrowdWisdomTrading.com.
Your job: produce a crisp marketing strategy + competitor analysis.
Output clean Markdown. Be specific, actionable, not generic.""",
        skills=["marketing_strategy"],
        max_iterations=2,
    )


def create_ads_scraper_agent() -> AgentLoop:
    """Create the Ads Scraper agent."""
    return AgentLoop(
        name="Ads Scraper",
        role="Meta Ads Scraping via Apify",
        system_prompt="""You are a direct-response advertising analyst.
Analyze scraped Meta ads and identify the top performing ones.
Output clean JSON.""",
        skills=["ads_analysis"],
        max_iterations=2,
    )


def create_pain_extractor_agent() -> AgentLoop:
    """Create the Pain Point Extractor agent."""
    return AgentLoop(
        name="Pain Extractor",
        role="Marketing Psychology Analysis",
        system_prompt="""You are a direct-response copywriter trained in Eugene Schwartz methodology.
You extract marketing psychology from successful ads.""",
        skills=["pain_extraction"],
        max_iterations=2,
    )


def create_ad_script_agent() -> AgentLoop:
    """Create the Ad Script Writer agent."""
    return AgentLoop(
        name="Ad Script Writer",
        role="Direct-Response Video Scripts",
        system_prompt="""You are a world-class direct-response video ad scriptwriter.
You write scripts for short-form video ads (30-60 sec) that convert.
You use proven frameworks: PAS (Problem-Agitate-Solution), AIDA, and hook-story-offer.""",
        skills=["ad_scripts"],
        max_iterations=2,
    )


def create_influencer_agent() -> AgentLoop:
    """Create the Influencer Outreach agent."""
    return AgentLoop(
        name="Influencer Outreach",
        role="Influencer Research & DM Drafting",
        system_prompt="""You are an influencer marketing specialist.
You research trading influencers and write personalized outreach.""",
        skills=["influencer_outreach"],
        max_iterations=2,
    )


def create_email_agent() -> AgentLoop:
    """Create the Email Sequence agent."""
    return AgentLoop(
        name="Email Sequence",
        role="Nurture Funnel Writer",
        system_prompt="""You are an email copywriter specializing in financial newsletters.
You write conversion-focused email sequences that turn free subscribers into paid members.""",
        skills=["email_sequence"],
        max_iterations=2,
    )


# ─── SKILL FILES ─────────────────────────────────────────────────────────────

SKILL_CONTENTS = {
    "marketing_strategy": """# Marketing Strategy Skill
## When to Use
When asked to create marketing strategy, competitor analysis, or buyer personas for a financial product.

## Procedure
1. Define 3 buyer personas with: name, age, job, frustration, willingness to pay
2. Identify top 3 acquisition channels with rationale and cost
3. Create 5 messaging angles (fear, aspiration, social proof, curiosity, FOMO)
4. Build a 30-day content calendar with weekly themes
5. Analyze competitors: positioning, price, weakness, how CrowdWisdom exploits it

## Output Format
Clean Markdown with headers, tables, and bullet points.
""",

    "ads_analysis": """# Ads Analysis Skill
## When to Use
When analyzing scraped Meta ads to identify winning patterns.

## Procedure
1. Filter ads by relevance (trading/finance keywords)
2. Score by: hook strength, value prop clarity, social proof, pain specificity
3. Select top 10 and explain why each was selected
4. Save as JSON with 'why_selected' field

## Output Format
JSON array with ad data and selection reasoning.
""",

    "pain_extraction": """# Pain Extraction Skill (Eugene Schwartz)
## When to Use
When extracting marketing psychology from successful ads.

## Procedure
1. Identify Core Pain Points (surface vs. deep emotional)
2. List Aspirations Being Sold (transformation, not features)
3. Extract Fear Triggers with direct ad quotes
4. Analyze Social Proof Patterns (numbers, testimonials, track records)
5. Build Power Words swipe file
6. Extract Hook Patterns as templates
7. Document CTA Patterns (urgency, curiosity, low risk)

## Frameworks
- Eugene Schwartz awareness levels (Unaware → Most Aware)
- PAS (Problem-Agitate-Solution)
- AIDA (Attention-Interest-Desire-Action)
""",

    "ad_scripts": """# Ad Script Writing Skill
## When to Use
When writing direct-response video ad scripts for financial products.

## Script Structure
- [HOOK] — First 3 seconds, grab attention
- [PROBLEM] — Name the pain
- [AGITATE] — Make it worse
- [SOLUTION] — Introduce the product
- [PROOF] — Social proof, numbers
- [CTA] — Clear call to action

## Format
- Label every line: [HOOK] [PROBLEM] [AGITATE] [SOLUTION] [CTA]
- B-roll direction in (parentheses)
- On-screen text in [brackets]
- Include word count and read time
""",

    "influencer_outreach": """# Influencer Outreach Skill
## When to Use
When researching influencers and writing personalized cold outreach.

## Research Checklist
- Full name and handle on each platform
- Follower count and engagement rate
- Content style and recent topics
- Whether they promote products
- Audience level (beginner/intermediate/experienced)
- Contact info (email, DM, business link)

## DM Structure (under 150 words)
1. Personalized opener (reference specific recent content)
2. Frame as opinion request, not collaboration pitch
3. Connect product to their audience's pain point
4. Specific low-friction ask
""",

    "email_sequence": """# Email Sequence Skill
## When to Use
When writing email nurture sequences for financial newsletter conversions.

## 5-Email Framework
1. Day 0: Welcome + first value delivery
2. Day 1: Founder story (vulnerability + discovery)
3. Day 3: Product demo in disguise (FOMO)
4. Day 4: Social proof (case studies)
5. Day 5: Urgency close (objection removal)

## For Each Email
- Subject line + A/B variant
- Preview text (50 chars)
- Full body (conversational, story-driven)
- CTA button text
- Estimated read time
""",
}


def ensure_skills_exist():
    """Create skill files if they don't exist."""
    os.makedirs(SKILLS_DIR, exist_ok=True)
    for name, content in SKILL_CONTENTS.items():
        skill_path = os.path.join(SKILLS_DIR, f"{name}.md")
        if not os.path.exists(skill_path):
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(content)


# Ensure skills are created on import
ensure_skills_exist()
