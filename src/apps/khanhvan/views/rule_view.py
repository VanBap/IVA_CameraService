import logging

from django.db.utils import IntegrityError

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common import drf
from common.drf import PageNumberPagination
from common.exceptions import ApplicationError

# === Vannhk ===
from ..serializers import rule_serializer, rule_version_serializer
from ..services import rule_service as service


logger = logging.getLogger('app')
DEFAULT_CAPTURE_TIME = 0

class RuleListView (APIView):
    class FilterSerializer(serializers.Serializer):
        name = serializers.CharField(required=False)
        type = serializers.IntegerField(required=False)

        start_time = serializers.TimeField(required=False)
        end_time = serializers.TimeField(required=False)

    class FilterDeleteSerializer(serializers.Serializer):
        rules = serializers.ListField(
            child=serializers.IntegerField(min_value=0)
        )

    OutputSerializer = rule_serializer.RuleWithCameraOutputSerializer
    InputSerializer = rule_serializer.RuleInputSerializer

    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        # get list of rules
        # === Dang viet do 21/01/25 ===
        rules = service.get_list_rules(validated_data)

        output_serializer_class = self.OutputSerializer

        # Neu co yeu cau hien thi tat ca
        if validated_data.get('all'):
            return Response(output_serializer_class(rules, many=True).data)

        # Neu khong co yeu cau hien thi tat ca
        return drf.get_paginated_response(
            pagination_class=PageNumberPagination,
            serializer_class=output_serializer_class,
            queryset=rules,
            request=request,
            view=self
        )


    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            # khong co tham so 'user'
            rule = service.create_rule(validated_data, user=request.user)
            return Response(self.OutputSerializer(rule).data, status=status.HTTP_201_CREATED)

        except IntegrityError as ex:
            logger.error('Failed to create rule %s', ex)
            raise ApplicationError({f'{str(ex)}': 'Database error'})

    def delete(self, request):
        filter_serializer = self.FilterDeleteSerializer(data= request.data)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data

        list_rule_ids = validated_data.get('rules')

        try:
            res = service.remove_list_rules(list_rule_ids)
            return Response(res)
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to bulk delete rule'})

class RuleDetailView(APIView):
    # OutputSerializer = rule_serializer.RuleDetailOutputSerializer
    OutputSerializer = rule_serializer.RuleDetailOutputSerializerV2
    InputSerializer = rule_serializer.RuleInputSerializer

    def get(self, request, pk):
        rule = service.get_rule_detail(pk)
        # print(f"Rule: {rule.id}, Camera: {rule.cameras}")

        res = self.OutputSerializer(rule).data

        return Response(res)

    def put(self, request, pk):
        serializer = self.InputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            rule = service.update_rule(pk, validated_data, user=request.user)
            return Response(rule_serializer.RuleWithCameraOutputSerializer(rule).data)
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Database error'})

    def delete(self, request, pk):
        try:
            service.remove_rule(pk)
            return Response({'message': 'Da xoa'})
        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to delete rule'})





class RuleVersionView(APIView):

    class FilterSerializer(serializers.Serializer):
        version_number = serializers.IntegerField(required=False)

    OutputSerializer = rule_version_serializer.RuleVersionGeneralOutputSerializer
    InputSerializer = rule_version_serializer.RuleVersionInputSerializer


    def get(self, request):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data


        rule_versions = service.get_list_rule_versions(validated_data)
        output_serializer_class = self.OutputSerializer

        if validated_data.get('all'):
            return Response(output_serializer_class(rule_versions, many=True).data)

        return drf.get_paginated_response(
            pagination_class=PageNumberPagination,
            serializer_class= output_serializer_class,
            queryset=rule_versions,
            request=request,
            view=self
        )

class RuleVersionDetailListView(APIView):

    OutputSerializer = rule_version_serializer.RuleVersionGeneralOutputSerializer
    InputSerializer = rule_version_serializer.RuleVersionInputSerializer

    def get(self, request, pk):

        # doi ten get_rule_version_detail_list
        rule_versions = service.get_rule_version_detail_list(pk)

        serialized_data = self.OutputSerializer(rule_versions, many=True).data

        # Trả về thêm thông tin count
        return Response({
            "count": len(serialized_data),
            "data": serialized_data
        })

    # === DELETE rule_version theo version_number ===
    def delete(self, request, pk):

        version_number = request.query_params.get("version_number")

        try:
            service.remove_rule_version_with_name(pk, version_number)
            return Response({'message': 'Da xoa thanh cong'})

        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to delete rule version'})


class RuleVersionDetailView(APIView):
    class FilterSerializer(serializers.Serializer):
        version_number = serializers.IntegerField(required=False)

    OutputSerializer = rule_version_serializer.RuleVersionOutputSerializer
    InputSerializer = rule_version_serializer.RuleVersionInputSerializer

    def get(self, request, rule_pk, version_pk):
        filter_serializer = self.FilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        validated_data = filter_serializer.validated_data


        rule_versions = service.get_rule_version_detail(validated_data, rule_pk, version_pk)
        serialized_data = self.OutputSerializer(rule_versions, many=True).data

        # Trả về thêm thông tin count
        return Response({
            "count": len(serialized_data),
            "data": serialized_data
        })
    # === DELETE rule_version theo version_id ===
    def delete(self, request, rule_pk, version_pk):

        try:
            service.remove_rule_version(rule_pk, version_pk)
            return Response({'message': 'Da xoa thanh cong'})

        except IntegrityError as ex:
            logger.exception(ex)
            raise ApplicationError({f'{str(ex)}': 'Failed to delete rule version'})






















