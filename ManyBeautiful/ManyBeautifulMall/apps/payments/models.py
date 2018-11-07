from django.db import models
from utils.models import BaseModel
from orders.models import OrderInfo


class Payment(BaseModel):
    """支付信息"""

    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name='订单')
    trade_id = models.CharField(max_length=200, unique=True, null=True, blank=True, verbose_name="支付流水号")

    class Meta:
        db_table = 'tb_payment'
        verbose_name = '支付信息'
        verbose_name_plural = verbose_name
