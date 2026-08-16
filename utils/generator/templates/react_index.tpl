/**
 * [[ name ]]模块（由低代码生成器生成）
 *
 * component key 与后端 system_menu.component 字段一一对应
 */
import { lazyPage } from '@/core/lazy'
import { defineModule } from '@/core/module'

const [[ Camel ]]Page = lazyPage(() => import('./pages/[[ Camel ]]Page'))

export default defineModule({
  name: '[[ code ]]',
  routes: [
    { component: '/[[ code ]]/index', element: [[ Camel ]]Page },
  ],
})
