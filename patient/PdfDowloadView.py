from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views import View
from patient.models import Prescription, Appointment
from .serializers import PdfSerializer


class pdf(View):
    def render_to_pdf(self,template_src, context_dict={}):
        template = get_template(template_src)
        html = template.render(context_dict)
        response = HttpResponse(content_type='application/pdf')
        pdf_status = pisa.CreatePDF(html, dest=response)

        if pdf_status.err:
            return HttpResponse('Some errors were encountered <pre>' + html + '</pre>')

        return response

    def ResultList(self,request,pk):
        template_name = "pdf_template.html"
        #name = request.GET.get('name')
        #age = request.GET.get('age')
        #print(request)
        #print(age)
        app = Appointment.objects.get(pk=pk)
        prescription = Prescription.objects.get(appointment=app)
        serializer=PdfSerializer(prescription)
        return self.render_to_pdf(
            template_name,
            serializer.data
        )
    
    def get(self, request,pk=None, format=None):
        t = self.ResultList(request,pk)
        return t
