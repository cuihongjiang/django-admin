/**
 * [[ name ]]接口（由低代码生成器生成）
 */
import { request } from '@/core/request'
import type { Paginated } from '@/core/types'

/** 实体类型命名加 Record 后缀，避免与 UI 组件（Button/Card 等）重名 */
export interface [[ Camel ]]Record {
  id: number
[% for f in entity_fields %]
  [[ f.field ]]: [[ f.ts_type ]]
[% endfor %]
}

export interface [[ Camel ]]Input {
[% for f in form_fields %]
  [[ f.field ]]?: [[ f.ts_type ]]
[% endfor %]
}

export const [[ camel ]]Api = {
  list: (params: Record<string, unknown>) =>
    request.get<Paginated<[[ Camel ]]Record>>('/[[ code ]]/', { params }),
  create: (data: [[ Camel ]]Input) => request.post<[[ Camel ]]Record>('/[[ code ]]/', data),
  update: (id: number, data: [[ Camel ]]Input) =>
    request.put<[[ Camel ]]Record>(`/[[ code ]]/${id}/`, data),
  remove: (id: number) => request.delete<null>(`/[[ code ]]/${id}/`),
}
