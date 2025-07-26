from django.http import JsonResponse
from core.models import Company

def get_contractors_by_business_type(request, business_type_id):
    """
    Return contractors matching the selected business type.
    """
    contractors = Company.objects.filter(
        is_contractor=True,
        business_type_id=business_type_id
    ).order_by('name')

    data = [
        {'id': contractor.id, 'name': contractor.name}
        for contractor in contractors
    ]

    return JsonResponse({'contractors': data})
