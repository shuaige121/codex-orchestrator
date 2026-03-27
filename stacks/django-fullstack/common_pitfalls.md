## Django Common Pitfalls

### 1. N+1 Queries
```python
# BAD: N additional queries
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # N queries!
# GOOD:
users = User.objects.select_related("profile").all()
```

### 2. fields = "__all__" in serializers
```python
# BAD: exposes password hash, is_superuser
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
# GOOD: explicit allowlist
        fields = ["id", "email", "first_name"]
```

### 3. Circular imports between apps
```python
# BAD: top-level cross-app model import causes circular import
# GOOD: use string reference in ForeignKey
user = models.ForeignKey("users.User", on_delete=models.CASCADE)
```

### 4. Fat views / skinny models
```python
# BAD: business logic in view
# GOOD: delegate to service layer
order = OrderService().create_order(serializer.validated_data, request.user)
```

### 5. Missing get_object_or_404
```python
# BAD: Model.objects.get() raises 500 on missing
# GOOD: get_object_or_404(Model, pk=pk) returns 404
```

### 6. Blocking sync calls in async views
```python
# BAD: User.objects.all() in async def — blocks event loop
# GOOD: use async ORM: [u async for u in User.objects.all()]
```

### 7. Hardcoding the User model
```python
# BAD: from django.contrib.auth.models import User
# GOOD: from django.contrib.auth import get_user_model
```

### 8. CASCADE on_delete without thinking
```python
# BAD: CASCADE deletes all orders when user deleted
# GOOD: use PROTECT or SET_NULL depending on domain
```

### 9. Missing database indexes on filtered fields
```python
# GOOD: db_index=True on frequently filtered fields, composite Index in Meta
```

### 10. print() instead of logging
```python
# GOOD: import logging; logger = logging.getLogger(__name__)
```
