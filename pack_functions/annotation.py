from decorators import transaction


@transaction('Create Linear Dimension')
def create_linear_dimension(
            doc, view, line, reference_array):
        return doc.Create.NewDimension(view, line, reference_array)

