




from rest_framework import serializers
from core_app.models import *



# admin profile serializer

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        field = "__all__"


class FilterNameSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = EmployeeDetail
        fields = ['user_id','first_name', 'last_name', 'designation', 'email','phone','address','gender']
        
        
        
class ProjectManagerNameSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = EmployeeDetail
        fields = ['user_id', 'first_name', 'last_name', 'designation', 'email', 'phone', 'address', 'gender']     
        
        
        
class EmployeeNameSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = EmployeeDetail
        fields = ['user_id', 'first_name', 'last_name', 'designation', 'email', 'phone', 'address', 'gender']
        
        
        
        
        
class AdminProfileSerializerView(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'created_at']       
        
        
        
# views.py

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from .serializers import AdminProfileSerializerView


class AdminProfileView(RetrieveAPIView):
    serializer_class = AdminProfileSerializerView
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # Returns currently authenticated user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()

        # Ensure the user is an admin
        if user.role != 'admin':
            return Response({
                "success": "False",
                "message": "You are not authorized to access this resource."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(user)
        return Response({
            "success": "True",
            "message": "Admin profile fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
        
        
class AdminProfileSerializerView(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'created_at']
        
        
         
         
         
class EmployeebirthdaySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDetail
        fields = '__all__'         
        
        
        
        
        
class AttendanceSummarySerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()       
    
    
class EmployeeListSerializerAdminView(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    attendance_status = serializers.SerializerMethodField()
   
    class Meta:
        model = EmployeeDetail
        fields = [
            "employee_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "designation",
            "department",
            "attendance_status",
           
        ]

    def get_attendance_status(self, obj):
        today = self.context.get("today")
        attendance = Attendance.objects.filter(employee=obj, date=today).first()
        if attendance and attendance.status == "Present":
            return "Active"
        return "Inactive"

    def get_status(self, obj):
        return True

    def get_message(self, obj):
        return "Data fetched successfully"
    
    
    
    
class EmployeeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDetail
        fields = "__all__"    
        
        
        
 
 
 
# class AttendanceSerializerempadmin(serializers.ModelSerializer):
#     class Meta:
#         model = Attendance
#         fields = "__all__"


from django.db.models import Min, Max,OuterRef,Subquery
import pytz
# serializers.py



from rest_framework import serializers
from django.utils import timezone
import pytz

class DailyAttendanceSerializer(serializers.Serializer):
    id = serializers.IntegerField()  # ✅ Attendance ID
    date = serializers.DateField()
    in_time = serializers.DateTimeField()
    out_time = serializers.DateTimeField()
    status = serializers.CharField()
    total_time = serializers.SerializerMethodField()
    overtime = serializers.SerializerMethodField()
    break_time = serializers.SerializerMethodField()  # ✅ Added static break time

    def get_total_time(self, instance):
        in_time = instance.get("in_time")
        out_time = instance.get("out_time")

        if in_time and out_time:
            total_time = out_time - in_time
            hours, remainder = divmod(total_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "0h 0m"

    def get_overtime(self, instance):
        out_time = instance.get("out_time")
        if out_time:
            cutoff = out_time.replace(hour=18, minute=0, second=0, microsecond=0)
            if out_time > cutoff:
                overtime = out_time - cutoff
                hours, remainder = divmod(overtime.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                return f"{hours}h {minutes}m"
        return "0h 0m"

    def get_break_time(self, instance):
        # ✅ Static break time of 1 hour 5 minutes
        return "1h 5m"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        ist = pytz.timezone("Asia/Kolkata")

        in_time = instance.get("in_time")
        out_time = instance.get("out_time")

        # Convert datetime to IST string format
        if in_time:
            in_time = timezone.localtime(in_time, ist)
            data["in_time"] = in_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["in_time"] = None

        if out_time:
            out_time = timezone.localtime(out_time, ist)
            data["out_time"] = out_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["out_time"] = None

        return data



class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    attendances = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDetail
        fields = ["id", "first_name", "last_name", "profile_pic", "employee_id", "attendances"]

    def get_attendances(self, obj):
        # Get the latest attendance status per date
        latest_status = (
            Attendance.objects.filter(employee=obj, date=OuterRef("date"))
            .order_by("-out_time")
            .values("status")[:1]
        )

        # ✅ Get the ID of the last out_time entry (to represent the daily record)
        latest_attendance_id = (
            Attendance.objects.filter(employee=obj, date=OuterRef("date"))
            .order_by("-out_time")
            .values("id")[:1]
        )

        # ✅ Annotate with in_time, out_time, status, and attendance ID
        qs = (
            Attendance.objects.filter(employee=obj)
            .values("date")
            .annotate(
                id=Subquery(latest_attendance_id),
                in_time=Min("in_time"),
                out_time=Max("out_time"),
                status=Subquery(latest_status),
            )
            .order_by("-date")
        )

        return DailyAttendanceSerializer(qs, many=True).data    
    
    
    
    
class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leave
        fields = [
            "id",
            "leave_type",
            "start_date",
            "end_date",
            "status",
            "approved_by",
            "attachments",
            "reason",
        ]


class BankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetail
        fields = "__all__"


class EmployeeDetailWithLeaveSerializer(serializers.ModelSerializer):
    taken = serializers.SerializerMethodField()
    total_leaves = serializers.SerializerMethodField()
    absent = serializers.SerializerMethodField()
    request = serializers.SerializerMethodField()
    lossofpay = serializers.SerializerMethodField()
    workeddays = serializers.SerializerMethodField()
    bank_details = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDetail
        fields = "__all__"
        extra_fields = [
            "leaves", "taken", "total_leaves", "absent",
            "request", "lossofpay", "workeddays", "bank_details"
        ]

    def get_taken(self, obj):
        approved_count = Leave.objects.filter(employee=obj, status="Approved").count()
        return approved_count if approved_count > 0 else "No leave taken"

    def get_request(self, obj):
        pending_count = Leave.objects.filter(employee=obj, status="Pending").count()
        return pending_count if pending_count > 0 else "No leave in request"

    def get_total_leaves(self, obj):
        return 16   # static for now

    def get_absent(self, obj):
        return 2    # static for now

    def get_workeddays(self, obj):
        return 240  # static for now

    def get_lossofpay(self, obj):
        return 2    # static for now

    def get_bank_details(self, obj):
        bank_details = BankDetail.objects.filter(employee=obj)
        if bank_details.exists():
            return BankDetailSerializer(bank_details, many=True).data
        return "No bank details found"
    
    
    

        
        
class HolidaySerializer1(serializers.ModelSerializer):
    # Show added_by user email (or full name if you want)
    added_by = serializers.CharField(source='added_by.first_name', read_only=True)

    class Meta:
        model = Holiday
        fields = ['id', 'description', 'date','type', 'added_by']   
        
from rest_framework import generics       
class NotificationLogSerializer(serializers.ModelSerializer):
    # Include user ID and username in the serialized output
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    # Convert timestamp to Indian time
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = ['id', 'user_id', 'user_name', 'action', 'title', 'timestamp']

    def get_timestamp(self, obj):
        # Convert UTC timestamp to IST
        ist = pytz.timezone('Asia/Kolkata')
        return obj.timestamp.astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')
    
    
    
    
class ProjectcountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'   
        
        
        
class AttendanceEditSerializer(serializers.ModelSerializer):
    total_time = serializers.SerializerMethodField()
    overtime = serializers.SerializerMethodField()
    break_time = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ["id", "employee", "date", "in_time", "out_time", "status", "total_time", "overtime", "break_time"]

    def validate(self, data):
        in_time = data.get("in_time")
        out_time = data.get("out_time")

        if in_time and out_time and out_time < in_time:
            raise serializers.ValidationError("Out time cannot be earlier than In time.")
        return data

    # ✅ Compute total working time
    def get_total_time(self, obj):
        in_time = obj.in_time
        out_time = obj.out_time
        if in_time and out_time:
            total_time = out_time - in_time
            hours, remainder = divmod(total_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{hours}h {minutes}m"
        return "0h 0m"

    # ✅ Compute overtime (after 6:00 PM)
    def get_overtime(self, obj):
        out_time = obj.out_time
        if out_time:
            cutoff = out_time.replace(hour=18, minute=0, second=0, microsecond=0)
            if out_time > cutoff:
                overtime = out_time - cutoff
                hours, remainder = divmod(overtime.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                return f"{hours}h {minutes}m"
        return "0h 0m"

    # ✅ Static break time (1 hour 5 minutes)
    def get_break_time(self, obj):
        return "1h 5m"

    # ✅ Format in_time and out_time in IST
    def to_representation(self, instance):
        data = super().to_representation(instance)
        ist = pytz.timezone("Asia/Kolkata")

        in_time = instance.in_time
        out_time = instance.out_time

        if in_time:
            in_time = timezone.localtime(in_time, ist)
            data["in_time"] = in_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["in_time"] = None

        if out_time:
            out_time = timezone.localtime(out_time, ist)
            data["out_time"] = out_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            data["out_time"] = None

        return data
    
    
class ProjectMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembers
        fields = ["team_leader", "project_manager", "tags"]


class TaskWithMembersSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.project_name", read_only=True)
    project_members = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status",
            "assigned_by", "assigned_to", "created_at", "updated_at",
            "project_name", "project_members"
        ]

    def get_project_members(self, obj):
        if obj.project:
            members = ProjectMembers.objects.filter(project=obj.project).first()
            if members:
                return ProjectMembersSerializer(members).data
        return None

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_updated_at(self, obj):
        if obj.updated_at:
            return obj.updated_at.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        return None 
         
           
        
        
        
        
# serializer 





                         
    


    
    
    
    
    
    
    
