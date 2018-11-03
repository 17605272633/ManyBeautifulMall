from haystack import indexes

# 继承可改
from .models import SKU


# 被搜索引擎建立索引的字段索引类
# 类名可改为:xxxxIndex
class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """SKU索引数据模型类"""

    # document=True: 表名该字段是主要进行关键字查询的字段
    # use_template=True: 表示通过模板来指明模型类字段
    # 在末班中指定搜索列 templates/search/indexes/模型类名称/模型类小写_text.txt
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建立索引的模型类"""
        # 模型类可改
        return SKU

    def index_queryset(self, using=None):
        """返回建立索引的数据查询集"""
        # is_launched 是否上架出售
        # 查询条件可修改
        return self.get_model().objects.filter(is_launched=True)
