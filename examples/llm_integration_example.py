"""
Example demonstrating LLM integration for enhanced recommendations.

This example shows how the LLM service enhances autocomplete and related query suggestions.
"""

import os
from app.services.llm_service import LLMService


def demonstrate_llm_features():
    """Demonstrate LLM service capabilities"""
    print("=" * 80)
    print("LLM Integration Example")
    print("=" * 80)
    print()
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - demonstrating with mock responses")
        print("   To use real LLM, set: export OPENAI_API_KEY='sk-...'")
        print()
        demonstrate_without_llm()
        return
    
    # Initialize LLM service
    print("1. Initializing LLM Service")
    print("-" * 80)
    llm = LLMService(
        provider="openai",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=150
    )
    
    if llm.is_available():
        print(f"✓ LLM service initialized with OpenAI/{llm.model}")
    else:
        print("✗ LLM service not available - check API key and internet connection")
        return
    
    print()
    
    # Example 1: Query Expansion
    print("2. Query Expansion")
    print("-" * 80)
    query = "销售分析"
    print(f"Original Query: '{query}'")
    print()
    
    expanded = llm.expand_query(query)
    if expanded:
        print(f"Expanded Queries ({len(expanded)}):")
        for i, exp_query in enumerate(expanded, 1):
            print(f"  {i}. {exp_query}")
    else:
        print("  (No expansion generated)")
    
    print()
    
    # Example 2: Query Expansion with Context
    print("3. Query Expansion with User Context")
    print("-" * 80)
    query = "市场趋势"
    context = {
        "user_history": ["销售分析", "客户满意度", "产品性能"],
        "domain": "business_intelligence"
    }
    print(f"Original Query: '{query}'")
    print(f"User History: {', '.join(context['user_history'])}")
    print()
    
    expanded_contextual = llm.expand_query(query, context=context)
    if expanded_contextual:
        print(f"Context-Aware Expanded Queries ({len(expanded_contextual)}):")
        for i, exp_query in enumerate(expanded_contextual, 1):
            print(f"  {i}. {exp_query}")
    else:
        print("  (No expansion generated)")
    
    print()
    
    # Example 3: Related Query Generation
    print("4. Related Query Generation")
    print("-" * 80)
    query = "竞争对手分析"
    print(f"Original Query: '{query}'")
    print()
    
    related = llm.generate_related_queries(query, limit=5)
    if related:
        print(f"Related Queries ({len(related)}):")
        for i, rel_query in enumerate(related, 1):
            print(f"  {i}. {rel_query['text']} (score: {rel_query['score']})")
            print(f"     Source: {rel_query['source']}, LLM: {rel_query['metadata']['llm_provider']}")
    else:
        print("  (No related queries generated)")
    
    print()
    
    # Example 4: Related Queries with Existing Results
    print("5. Related Queries Avoiding Duplicates")
    print("-" * 80)
    query = "客户满意度"
    existing = ["客户反馈", "用户体验", "服务质量"]
    print(f"Original Query: '{query}'")
    print(f"Existing Results: {', '.join(existing)}")
    print()
    
    related_filtered = llm.generate_related_queries(
        query,
        existing_results=existing,
        limit=5
    )
    if related_filtered:
        print(f"New Related Queries ({len(related_filtered)}):")
        for i, rel_query in enumerate(related_filtered, 1):
            print(f"  {i}. {rel_query['text']} (score: {rel_query['score']})")
    else:
        print("  (No new related queries generated)")
    
    print()
    
    # Example 5: Query Rewriting
    print("6. Query Rewriting")
    print("-" * 80)
    query = "销售"
    print(f"Original Query: '{query}'")
    print()
    
    for intent in ["clarify", "expand", "formalize"]:
        rewritten = llm.rewrite_query(query, intent=intent)
        if rewritten:
            print(f"  {intent.capitalize()}: '{rewritten}'")
    
    print()
    
    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print("The LLM service enhances recommendations by:")
    print("  • Expanding queries with semantically related terms")
    print("  • Generating contextually relevant follow-up questions")
    print("  • Understanding user intent beyond keyword matching")
    print("  • Adapting suggestions based on conversation history")
    print()
    print("Integration Benefits:")
    print("  ✓ Broader search coverage through query expansion")
    print("  ✓ More intelligent related query suggestions")
    print("  ✓ Better handling of ambiguous or short queries")
    print("  ✓ Personalized recommendations based on context")
    print()


def demonstrate_without_llm():
    """Demonstrate what happens without LLM"""
    print("=" * 80)
    print("System Behavior WITHOUT LLM")
    print("=" * 80)
    print()
    
    print("Without LLM integration, the system uses:")
    print()
    print("1. Hybrid Search")
    print("   - Keyword matching: Exact and prefix matches")
    print("   - Vector search: Semantic similarity using embeddings")
    print("   - Combined scoring with configurable weights")
    print()
    print("2. Personalization")
    print("   - User's historical selections")
    print("   - Query-specific preferences")
    print("   - Global popularity trends")
    print()
    print("3. Query Sequences")
    print("   - Tracks query chains (A→B→C)")
    print("   - Suggests 'next' and 'previous' queries")
    print("   - Based on actual user behavior patterns")
    print()
    print("=" * 80)
    print("System Behavior WITH LLM (when enabled)")
    print("=" * 80)
    print()
    print("All of the above PLUS:")
    print()
    print("4. LLM-Enhanced Query Expansion")
    print("   - Generates semantically related search terms")
    print("   - Understands synonyms and related concepts")
    print("   - Context-aware based on user history")
    print()
    print("5. LLM-Generated Related Queries")
    print("   - Intelligent follow-up questions")
    print("   - Natural conversation flow")
    print("   - Domain-specific suggestions")
    print()
    print("6. Query Understanding")
    print("   - Intent classification")
    print("   - Query refinement and clarification")
    print("   - Natural language processing")
    print()


def show_integration_benefits():
    """Show concrete examples of LLM benefits"""
    print()
    print("=" * 80)
    print("Real-World Examples")
    print("=" * 80)
    print()
    
    examples = [
        {
            "query": "销售",
            "without_llm": [
                "销售额",
                "销售数据",
                "销售趋势"
            ],
            "with_llm": [
                "销售额",
                "营业收入分析",  # LLM understands synonyms
                "销售业绩评估",  # LLM adds context
                "市场占有率",    # LLM suggests related concepts
                "客户转化率"     # LLM finds logical connections
            ]
        },
        {
            "query": "customer satisfaction",
            "without_llm": [
                "customer satisfaction score",
                "customer feedback",
                "satisfaction survey"
            ],
            "with_llm": [
                "customer satisfaction score",
                "Net Promoter Score (NPS)",      # LLM knows domain terms
                "customer retention rate",        # LLM connects concepts
                "service quality metrics",        # LLM expands scope
                "customer lifetime value (CLV)"  # LLM suggests related KPIs
            ]
        },
        {
            "query": "趋势",
            "without_llm": [
                "趋势分析",
                "趋势预测",
                "市场趋势"
            ],
            "with_llm": [
                "趋势分析与预测",       # LLM clarifies intent
                "时间序列分析",         # LLM adds technical terms
                "增长率变化趋势",       # LLM provides specificity
                "季节性波动分析",       # LLM suggests related aspects
                "未来发展趋势预判"      # LLM adds forward-looking view
            ]
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"Example {i}: '{example['query']}'")
        print("-" * 40)
        print("Without LLM:")
        for item in example["without_llm"]:
            print(f"  • {item}")
        print()
        print("With LLM (more comprehensive):")
        for item in example["with_llm"]:
            print(f"  • {item}")
        print()
    
    print("=" * 80)
    print("Key Advantages:")
    print("  1. Semantic Understanding: Goes beyond keyword matching")
    print("  2. Domain Knowledge: Understands business intelligence terminology")
    print("  3. Contextual Awareness: Considers conversation flow")
    print("  4. Creative Suggestions: Discovers non-obvious connections")
    print("  5. Natural Language: Better handles conversational queries")
    print()


if __name__ == "__main__":
    demonstrate_llm_features()
    show_integration_benefits()
    
    print("=" * 80)
    print("To enable LLM in your service:")
    print("=" * 80)
    print()
    print("1. Install dependencies:")
    print("   pip install openai>=1.0.0")
    print()
    print("2. Set API key:")
    print("   export OPENAI_API_KEY='sk-...'")
    print()
    print("3. Enable in config.yaml:")
    print("   llm:")
    print("     enabled: true")
    print("     provider: openai")
    print("     model: gpt-3.5-turbo")
    print()
    print("See LLM_INTEGRATION.md for detailed documentation.")
    print()
