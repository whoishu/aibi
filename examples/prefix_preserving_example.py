"""Example demonstrating prefix-preserving autocomplete feature

This example shows how the new prefix-preserving autocomplete works
for long queries where the user wants to preserve the full context.

Example: "帮我查询一下今年北京的销" should complete to:
- "帮我查询一下今年北京的销售额"
- "帮我查询一下今年北京的销量"
- "帮我查询一下今年北京的销售情况"
"""

from unittest.mock import Mock
from app.services.prefix_preserving_service import PrefixPreservingService


def main():
    print("=" * 70)
    print("Prefix-Preserving Autocomplete Example")
    print("=" * 70)
    print()

    # Create mock services for demonstration
    mock_opensearch = Mock()
    mock_opensearch.keyword_search.return_value = [
        {"text": "销售额分析报告", "score": 0.9},
        {"text": "销量统计", "score": 0.85},
        {"text": "销售情况总结", "score": 0.8},
        {"text": "销售数据", "score": 0.75},
    ]

    mock_llm = Mock()
    mock_llm.is_available.return_value = True
    mock_llm.rank_prefix_completions.return_value = [
        {
            "text": "帮我查询一下今年北京的销售额",
            "score": 0.95,
            "method": "llm_ranked",
            "completed_term": "销售额",
            "reason": "Most common query pattern for sales data",
        },
        {
            "text": "帮我查询一下今年北京的销量",
            "score": 0.92,
            "method": "llm_ranked",
            "completed_term": "销量",
            "reason": "Related metric often queried",
        },
        {
            "text": "帮我查询一下今年北京的销售情况",
            "score": 0.88,
            "method": "llm_ranked",
            "completed_term": "销售情况",
            "reason": "Comprehensive overview request",
        },
        {
            "text": "帮我查询一下今年北京的销售数据",
            "score": 0.85,
            "method": "llm_ranked",
            "completed_term": "销售数据",
            "reason": "Raw data request",
        },
    ]

    # Create service
    service = PrefixPreservingService(
        opensearch_service=mock_opensearch,
        llm_service=mock_llm,
        personalization_service=None,
    )

    # Test queries
    test_queries = [
        "销售",  # Too short, should not trigger prefix mode
        "帮我查询一下今年北京的销",  # Long query, should trigger prefix mode
        "请分析一下上个季度的市场占",  # Another long query example
    ]

    for query in test_queries:
        print(f"Query: '{query}'")
        print("-" * 70)

        # Analyze input
        analysis = service.analyze_input(query)
        print(f"Analysis:")
        print(f"  - Tokens: {analysis['tokens']}")
        print(f"  - Is long query: {analysis['is_long_query']}")
        print(f"  - Prefix: '{analysis['prefix']}'")
        print(f"  - Incomplete term: '{analysis['incomplete_term']}'")
        print()

        # Get suggestions
        suggestions = service.get_suggestions_with_prefix_preservation(
            query=query,
            user_id=None,
            limit=5,
        )

        if suggestions:
            print(f"Suggestions (prefix-preserved):")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion.text}")
                print(f"     Score: {suggestion.score}")
                print(f"     Method: {suggestion.metadata.get('method', 'N/A')}")
                if suggestion.metadata.get("reason"):
                    print(f"     Reason: {suggestion.metadata['reason']}")
                print()
        else:
            print("No prefix-preserved suggestions (query too short or no candidates)")
            print()

        print()

    # Show how it works step by step
    print("=" * 70)
    print("Step-by-Step Workflow for Long Query")
    print("=" * 70)
    print()

    query = "帮我查询一下今年北京的销"
    print(f"User Input: '{query}'")
    print()

    # Step 1: Tokenization
    analysis = service.analyze_input(query)
    print("Step 1: Tokenization (using jieba)")
    print(f"  Tokens: {analysis['tokens']}")
    print()

    # Step 2: Identify prefix and incomplete term
    print("Step 2: Identify Prefix and Incomplete Term")
    print(f"  Prefix: '{analysis['prefix']}'")
    print(f"  Incomplete term: '{analysis['incomplete_term']}'")
    print()

    # Step 3: Search candidates
    print("Step 3: Search OpenSearch for Completion Candidates")
    candidates = service.search_completion_candidates(
        analysis["incomplete_term"], limit=20
    )
    print(f"  Found {len(candidates)} candidates:")
    for candidate in candidates[:5]:
        print(f"    - {candidate}")
    print()

    # Step 4: LLM ranking
    print("Step 4: LLM Ranks and Generates Complete Suggestions")
    results = service.rank_and_complete(
        prefix=analysis["prefix"],
        incomplete_term=analysis["incomplete_term"],
        candidates=candidates,
    )
    print(f"  LLM returned {len(results)} ranked completions:")
    for i, result in enumerate(results, 1):
        print(f"    {i}. '{result['text']}'")
        print(f"       Score: {result['score']}")
        if result.get("reason"):
            print(f"       Reason: {result['reason']}")
    print()

    print("=" * 70)
    print("Feature Benefits:")
    print("=" * 70)
    print("✓ Preserves full user context in long queries")
    print("✓ Uses jieba for accurate Chinese tokenization")
    print("✓ LLM provides semantic understanding for ranking")
    print("✓ Falls back gracefully when LLM is unavailable")
    print("✓ Seamlessly integrated into existing autocomplete flow")
    print()


if __name__ == "__main__":
    main()
