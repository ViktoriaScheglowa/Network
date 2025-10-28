from rest_framework import serializers
from .models import NetworkNode, Product, NetworkNodeProduct


class ProductSerializer(serializers.ModelSerializer):
    """Serializer для продуктов"""

    network_nodes = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "model", "release_date", "created_at", "network_nodes"]
        read_only_fields = ["created_at"]

    def get_network_nodes(self, obj):
        # Получаем информацию о узлах, где есть этот продукт
        node_products = obj.networknodeproduct_set.select_related("network_node").all()
        return [
            {
                "node_id": np.network_node.id,
                "node_name": np.network_node.name,
                "price": float(np.price) if np.price else 0,
                "quantity": np.quantity,
                "is_available": np.is_available,
            }
            for np in node_products
        ]


class NetworkNodeProductSerializer(serializers.ModelSerializer):
    """Serializer для связи узел-продукт"""

    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )

    class Meta:
        model = NetworkNodeProduct
        fields = [
            "id",
            "product",
            "product_id",
            "price",
            "quantity",
            "is_available",
            "added_at",
        ]
        read_only_fields = ["added_at"]


class NetworkNodeSerializer(serializers.ModelSerializer):
    """Serializer для чтения узлов сети"""

    hierarchy_level = serializers.ReadOnlyField()
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    products_info = NetworkNodeProductSerializer(
        source="networknodeproduct_set", many=True, read_only=True
    )

    class Meta:
        model = NetworkNode
        fields = [
            "id",
            "name",
            "node_type",
            "email",
            "country",
            "city",
            "street",
            "house_number",
            "supplier",
            "supplier_name",
            "debt",
            "created_at",
            "is_active",
            "hierarchy_level",
            "products_info",
        ]
        read_only_fields = ["debt", "created_at", "hierarchy_level"]


class NetworkNodeCreateSerializer(serializers.ModelSerializer):
    """Serializer для создания и обновления узлов сети"""

    products = serializers.ListField(
        child=serializers.DictField(), required=False, write_only=True
    )

    class Meta:
        model = NetworkNode
        fields = "__all__"
        read_only_fields = ["debt"]

    def create(self, validated_data):
        products_data = validated_data.pop("products", [])
        network_node = NetworkNode.objects.create(**validated_data)

        # Создание связей с продуктами
        for product_data in products_data:
            NetworkNodeProduct.objects.create(
                network_node=network_node,
                product_id=product_data.get("product_id"),
                price=product_data.get("price"),
                quantity=product_data.get("quantity", 0),
                is_available=product_data.get("is_available", True),
            )

        return network_node

    def update(self, instance, validated_data):
        products_data = validated_data.pop("products", None)

        # Обновление полей узла
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновление продуктов если предоставлены
        if products_data is not None:
            # Удаляем старые связи
            instance.networknodeproduct_set.all().delete()

            # Создаем новые связи
            for product_data in products_data:
                NetworkNodeProduct.objects.create(
                    network_node=instance,
                    product_id=product_data.get("product_id"),
                    price=product_data.get("price"),
                    quantity=product_data.get("quantity", 0),
                    is_available=product_data.get("is_available", True),
                )

        return instance

    def validate_products(self, value):
        """Валидация данных продуктов"""
        for product_data in value:
            if "product_id" not in product_data:
                raise serializers.ValidationError(
                    "Каждый продукт должен иметь product_id"
                )
        return value
