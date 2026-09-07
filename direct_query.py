import json
from django.db import connection
from django.http import JsonResponse


def FamilyVillageApi(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            action = body.get("action", "").strip().upper()
            table_name = body.get("tableName", "").strip().upper()
            name = body.get("Name", "").strip()

            # ✅ FETCH FAMILY BY VILLAGE
            if action == "FETCHFAMILYBYVILLAGE" and table_name == "FAMILYMASTER":

                with connection.cursor() as cursor:
                    query = """
                        SELECT 
                            FM.FamilyID AS FamilyId,
                            FM.HeadName,
                            FM.Gam,
                            M.MemberID AS MemberId,
                            M.Name AS FullName
                        FROM FamilyMaster FM
                        LEFT JOIN FamilyMembers M 
                            ON FM.FamilyID = M.FamilyID
                        WHERE LOWER(LTRIM(RTRIM(FM.Gam))) = LOWER(LTRIM(RTRIM(%s)))
                        ORDER BY FM.HeadName ASC
                    """

                    cursor.execute(query, [name])

                    columns = [col[0] for col in cursor.description]
                    data = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]

                return JsonResponse({
                    "status": True,
                    "data": data
                })

            return JsonResponse({
                "status": False,
                "message": "Invalid action or table"
            })

        except Exception as e:
            return JsonResponse({
                "status": False,
                "error": str(e)
            })

    return JsonResponse({
        "status": False,
        "message": "Only POST allowed"
    })


def sp_22Gam(action, role=None, village=None):
    with connection.cursor() as cursor:

        cursor.execute("""
            EXEC sp_DashboardCounts
            @Action=%s,
            @Role=%s,
            @Village=%s
        """, [action, role, village])

        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in results]

    return data
