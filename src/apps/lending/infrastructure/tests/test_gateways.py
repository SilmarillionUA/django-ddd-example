from catalog.domain.choices import CopyCondition
from lending.infrastructure.gateways import CatalogGateway


def test_gateway_follows_catalog_lendable_rule(make_copy):
    copy_obj = make_copy()
    copy_obj.condition = CopyCondition.DAMAGED
    copy_obj.save()

    gateway = CatalogGateway()

    assert gateway.copy_id_for_barcode(barcode=copy_obj.barcode) == copy_obj.pk
    assert not gateway.is_lendable(copy_id=copy_obj.pk)
    assert gateway.copy_id_for_barcode(barcode="missing") is None
