def count_documents(doc_cls, my_filter, max_count):
    if max_count == 0:
        # no count
        return 0
    elif max_count < 0:
        # count all
        return doc_cls.objects.filter(my_filter).count()

    pipeline = [
        {
            '$match': my_filter.to_query(doc_cls)
        },
        {
            '$limit': max_count
        },
        {
            '$group': {
                '_id': None,
                'total': {"$sum": 1}
            }
        }
    ]

    results = doc_cls.objects().aggregate(pipeline)
    if results:
        for data in results:
            return data['total']

    return 0
