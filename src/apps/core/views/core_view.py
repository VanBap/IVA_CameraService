from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from utils import misc, minio_utils

class UploadFileView(APIView):
    def post(self, request):  # noqa
        file = request.FILES["file"]
        uploaded_path = file.object_name
        return Response({'url': minio_utils.MinioUtil.get_absolute_url(uploaded_path)}, status=status.HTTP_201_CREATED)


class Base64View(APIView):
    class FilterSerializer(serializers.Serializer):
        url = serializers.CharField()

    def post(self, request):  # noqa
        serializer = self.FilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data['url']

        return Response(misc.get_base64_from_file(url))
