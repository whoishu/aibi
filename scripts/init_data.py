"""Script to initialize sample data for testing"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from app.utils.config import get_config
from app.services.opensearch_service import OpenSearchService
from app.services.vector_service import VectorService
from app.services.autocomplete_service import AutocompleteService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create sample data for autocomplete"""
    
    # Sample queries and keywords (Chinese and English mixed)
    sample_data = [
        {"text": "销售额", "keywords": ["sales", "revenue", "销售"]},
        {"text": "销售额趋势分析", "keywords": ["sales", "trend", "analysis", "销售", "趋势"]},
        {"text": "销售额同比增长率", "keywords": ["sales", "yoy", "growth", "销售", "增长"]},
        {"text": "销售额环比增长率", "keywords": ["sales", "mom", "growth", "销售"]},
        {"text": "各地区销售额排名", "keywords": ["sales", "region", "ranking", "销售", "地区"]},
        {"text": "产品销量", "keywords": ["product", "sales volume", "产品", "销量"]},
        {"text": "产品销量排行榜", "keywords": ["product", "sales", "ranking", "产品", "销量"]},
        {"text": "用户数量", "keywords": ["user", "count", "用户", "数量"]},
        {"text": "用户增长趋势", "keywords": ["user", "growth", "trend", "用户", "增长"]},
        {"text": "活跃用户数", "keywords": ["active", "user", "活跃", "用户"]},
        {"text": "新增用户", "keywords": ["new", "user", "新增", "用户"]},
        {"text": "客户转化率", "keywords": ["customer", "conversion", "rate", "客户", "转化率"]},
        {"text": "订单量", "keywords": ["order", "count", "订单", "数量"]},
        {"text": "订单金额", "keywords": ["order", "amount", "订单", "金额"]},
        {"text": "订单量趋势", "keywords": ["order", "trend", "订单", "趋势"]},
        {"text": "平均订单金额", "keywords": ["average", "order", "amount", "平均", "订单"]},
        {"text": "退货率", "keywords": ["return", "rate", "退货率"]},
        {"text": "客单价", "keywords": ["average", "order", "value", "客单价"]},
        {"text": "利润率", "keywords": ["profit", "margin", "利润率"]},
        {"text": "毛利率", "keywords": ["gross", "profit", "margin", "毛利率"]},
        {"text": "净利润", "keywords": ["net", "profit", "净利润"]},
        {"text": "成本分析", "keywords": ["cost", "analysis", "成本", "分析"]},
        {"text": "库存周转率", "keywords": ["inventory", "turnover", "库存", "周转率"]},
        {"text": "存货天数", "keywords": ["inventory", "days", "存货", "天数"]},
        {"text": "各产品类别销售占比", "keywords": ["product", "category", "sales", "ratio", "产品", "类别", "占比"]},
        {"text": "营销效果分析", "keywords": ["marketing", "effect", "analysis", "营销", "效果"]},
        {"text": "渠道转化率", "keywords": ["channel", "conversion", "rate", "渠道", "转化率"]},
        {"text": "流量来源分析", "keywords": ["traffic", "source", "analysis", "流量", "来源"]},
        {"text": "用户留存率", "keywords": ["user", "retention", "rate", "用户", "留存率"]},
        {"text": "用户流失率", "keywords": ["user", "churn", "rate", "用户", "流失率"]},
        {"text": "复购率", "keywords": ["repurchase", "rate", "复购率"]},
        {"text": "客户生命周期价值", "keywords": ["customer", "lifetime", "value", "CLV", "客户", "生命周期"]},
        {"text": "市场份额", "keywords": ["market", "share", "市场", "份额"]},
        {"text": "竞品分析", "keywords": ["competitor", "analysis", "竞品", "分析"]},
        {"text": "价格敏感度分析", "keywords": ["price", "sensitivity", "价格", "敏感度"]},
        {"text": "会员数量", "keywords": ["member", "count", "会员", "数量"]},
        {"text": "会员等级分布", "keywords": ["member", "level", "distribution", "会员", "等级"]},
        {"text": "今日销售额", "keywords": ["today", "sales", "今日", "销售额"]},
        {"text": "本周销售额", "keywords": ["week", "sales", "本周", "销售额"]},
        {"text": "本月销售额", "keywords": ["month", "sales", "本月", "销售额"]},
        {"text": "本季度销售额", "keywords": ["quarter", "sales", "本季度", "销售额"]},
        {"text": "本年度销售额", "keywords": ["year", "sales", "本年度", "销售额"]},
        {"text": "品牌销售排行", "keywords": ["brand", "sales", "ranking", "品牌", "销售", "排行"]},
        {"text": "店铺销售排行", "keywords": ["store", "sales", "ranking", "店铺", "销售", "排行"]},
        {"text": "销售员业绩排名", "keywords": ["salesperson", "performance", "ranking", "销售员", "业绩"]},
        {"text": "库存预警", "keywords": ["inventory", "alert", "库存", "预警"]},
        {"text": "畅销商品", "keywords": ["bestseller", "product", "畅销", "商品"]},
        {"text": "滞销商品", "keywords": ["slow-moving", "product", "滞销", "商品"]},
        {"text": "促销活动效果", "keywords": ["promotion", "effect", "促销", "活动", "效果"]},
        {"text": "优惠券使用率", "keywords": ["coupon", "usage", "rate", "优惠券", "使用率"]},
    ]
    
    return sample_data


def main():
    """Main function"""
    logger.info("Initializing sample data...")
    
    try:
        # Load configuration
        config = get_config()
        
        # Initialize services
        vector_service = VectorService(model_name=config.vector_model.model_name)
        
        opensearch_service = OpenSearchService(
            host=config.opensearch.host,
            port=config.opensearch.port,
            use_ssl=config.opensearch.use_ssl,
            verify_certs=config.opensearch.verify_certs,
            username=config.opensearch.username,
            password=config.opensearch.password,
            index_name=config.opensearch.index_name,
            vector_dimension=config.vector_model.dimension
        )
        
        # Check connection
        if not opensearch_service.check_connection():
            logger.error("Cannot connect to OpenSearch. Please ensure OpenSearch is running.")
            return
        
        # Create index
        logger.info("Creating index...")
        opensearch_service.create_index()
        
        # Initialize autocomplete service
        autocomplete_service = AutocompleteService(
            opensearch_service=opensearch_service,
            vector_service=vector_service,
            personalization_service=None
        )
        
        # Add sample data
        logger.info("Adding sample data...")
        sample_data = create_sample_data()
        
        success, errors = autocomplete_service.add_documents_bulk(sample_data)
        
        logger.info(f"Successfully added {success} documents with {errors} errors")
        logger.info("Sample data initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing data: {e}")
        raise


if __name__ == "__main__":
    main()
