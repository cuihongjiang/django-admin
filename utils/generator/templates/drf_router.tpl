# 将下面两行分别加入 apps/router.py（由低代码生成器生成）

from apps.[[ app_label ]].apis.[[ code ]] import [[ model_name ]]ViewSet

api_router.register(r'[[ code ]]', [[ model_name ]]ViewSet, basename='[[ code ]]')
