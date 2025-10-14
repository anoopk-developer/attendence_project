




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
        
        
        
        
        
# admin profile serializer
class AdminProfileSerializerView(serializers.ModelSerializer):
    class Meta:
        model = EmployeeDetail
        fields = '__all__'
        
        
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
    
    
    
    
class TaskSerializerneww(serializers.ModelSerializer):
    assigned_by_name = serializers.CharField(source="assigned_by.username", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "status",
            "assigned_by_name", "assigned_to_name",
            "created_at", "due_date", "updated_at"
        ]


class ProjectMembersSerializerneww(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembers
        fields = ["id", "team_leader", "project_manager", "tags"]


class ProjectDetailSerializerneww(serializers.ModelSerializer):
    project_members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "project_logo", "project_name", "client", "start_date", "end_date",
            "priority", "project_value", "total_working_hours", "extra_time",
            "status", "description", "attachment", "reason_for_rejection",
            "project_members", "tasks"
        ]

    def get_project_members(self, obj):
        members = ProjectMembers.objects.filter(project=obj)
        return ProjectMembersSerializerneww(members, many=True).data

    def get_tasks(self, obj):
        tasks = Task.objects.filter(project=obj)
        return TaskSerializerneww(tasks, many=True).data    
    
    
    
    
class ProjectFileSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = ProjectFile
        fields = ['id', 'project', 'project_name', 'file', 'uploaded_at']
         
           
        
# project image serializer
class ProjectImageSerializer(serializers.ModelSerializer):  
    class Meta:
        model = ProjectImages
        fields = ['id', 'project', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']     
        
 
 
# branch serializer
class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__' 
 
 
 
 
        
        
from datetime import date, timedelta       
class EmployeeAttendanceSerializerpast7days(serializers.ModelSerializer):
    attendances = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDetail
        fields = ["id", "first_name", "last_name", "profile_pic", "employee_id", "attendances"]

    def get_attendances(self, obj):
        today = date.today()
        last_7_days = today - timedelta(days=7)

        # Filter attendance only for the past 7 days (including today)
        attendance_qs = Attendance.objects.filter(
            employee=obj,
            date__range=[last_7_days, today]
        )

        # Subqueries for latest status and ID of the day's last record
        latest_status = (
            Attendance.objects.filter(employee=obj, date=OuterRef("date"))
            .order_by("-out_time")
            .values("status")[:1]
        )
        latest_attendance_id = (
            Attendance.objects.filter(employee=obj, date=OuterRef("date"))
            .order_by("-out_time")
            .values("id")[:1]
        )

        # Annotate daily summary
        qs = (
            attendance_qs
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
    
    
    
    
    
    
class AttendanceLeaveSummarydiagramSerializer(serializers.Serializer):
    absent_count = serializers.IntegerField()
    leave_count = serializers.IntegerField()
    sick_leave_count = serializers.IntegerField()
    wfh_count = serializers.IntegerField()
    on_time_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    
    
class WorkinghoursfractionSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    today_total_hours = serializers.SerializerMethodField()  # new field

    class Meta:
        model = Attendance
        fields = [
            'id',
            'employee_name',
            'in_time',
            'out_time',
            'today_total_hours',  # include total hours in response
        ]

    def get_today_total_hours(self, obj):
        if obj.in_time and obj.out_time:
            delta = obj.out_time - obj.in_time
            worked_hours = delta.total_seconds() / 3600  # convert seconds to hours
            worked_hours_rounded = round(worked_hours, 2)
            # return as fraction of 9-hour day (adjust as needed)
            return f"{worked_hours_rounded} / 9 hrs"
        return "0.0 / 9 hrs"
    
    
    
class WeeklyWorkinghoursSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    weekly_total_hours = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'employee_name',
            'weekly_total_hours',
        ]

    def get_weekly_total_hours(self, obj):
        # 'obj' will be Attendance instance but we'll use context to pass total
        total_seconds = getattr(obj, 'weekly_seconds', 0)
        worked_hours = total_seconds / 3600
        worked_hours_rounded = round(worked_hours, 2)
        return f"{worked_hours_rounded} / 45 hrs"  # Assuming 9hrs/day * 5days



class EmployeeDetaileditSerializer(serializers.ModelSerializer):
    taken = serializers.SerializerMethodField()
    total_leaves = serializers.SerializerMethodField()
    absent = serializers.SerializerMethodField()
    request = serializers.SerializerMethodField()
    lossofpay = serializers.SerializerMethodField()
    workeddays = serializers.SerializerMethodField()
    bank_details = BankDetailSerializer(many=True, required=False)

    class Meta:
        model = EmployeeDetail
        fields = "__all__"
        extra_fields = [
            "leaves", "taken", "total_leaves", "absent",
            "request", "lossofpay", "workeddays", "bank_details"
        ]

    # --- Custom Fields ---
    def get_taken(self, obj):
        approved_count = Leave.objects.filter(employee=obj, status="Approved").count()
        return approved_count if approved_count > 0 else "No leave taken"

    def get_request(self, obj):
        pending_count = Leave.objects.filter(employee=obj, status="Pending").count()
        return pending_count if pending_count > 0 else "No leave in request"

    def get_total_leaves(self, obj):
        return 16  # static

    def get_absent(self, obj):
        return 2  # static

    def get_workeddays(self, obj):
        return 240  # static

    def get_lossofpay(self, obj):
        return 2  # static

    # --- Custom Update for nested Bank Details ---
    def update(self, instance, validated_data):
        bank_data_list = validated_data.pop("bank_details", None)

        # Update Employee basic details
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Bank Details if provided
        if bank_data_list is not None:
            # Clear old bank details and re-add
            BankDetail.objects.filter(employee=instance).delete()
            for bank_data in bank_data_list:
                BankDetail.objects.create(employee=instance, **bank_data)

        return instance    
    
    

class ProjectMemberslistSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = ProjectMembers
        fields = ['id', 'project_name', 'team_leader', 'project_manager', 'tags']
        
        
        
# privacy policy serializers
class PrivacyPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivacyPolicy
        fields = '__all__'        
        
        
        
        
class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = '__all__'              
        
    
class AboutsessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'              
            
    

    

        
           
        
        
# serializer 





                         
    


    
    
    
    
    
    
    
