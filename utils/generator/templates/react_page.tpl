/**
 * [[ name ]]管理页：搜索 + TanStack Table 分页列表 + 新增/编辑弹窗 + 删除
 * 由低代码生成器生成，可在此基础上精修
 */
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
} from '@tanstack/react-table'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useForm, type Resolver } from 'react-hook-form'
import { toast } from 'sonner'
import { z } from 'zod'

import { Auth } from '@/core/components/auth'
[% if dict_codes %]
import { useDict } from '@/core/hooks/use-dict'
[% endif %]

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
[% if has_select %]
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
[% endif %]
[% if has_switch %]
import { Switch } from '@/components/ui/switch'
[% endif %]
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

import { [[ camel ]]Api, type [[ Camel ]]Record } from '../api'

const formSchema = z.object({
[% for f in form_fields %]
  [[ f.field ]]: [[ f.zod_rule ]],
[% endfor %]
})

type FormValues = z.infer<typeof formSchema>

export default function [[ Camel ]]Page() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState<Record<string, string>>({})
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [editing, setEditing] = useState<[[ Camel ]]Record | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleting, setDeleting] = useState<[[ Camel ]]Record | null>(null)

[% for dc in dict_codes %]
  const { data: dict[[ dc|camel ]] } = useDict('[[ dc ]]')
  const dictLabel[[ dc|camel ]] = (v: unknown) =>
    dict[[ dc|camel ]]?.find((i) => i.value === String(v))?.label ?? String(v ?? '-')
[% endfor %]

  // 字典 label 列依赖组件内的 useDict，故列定义置于组件内
  const columnsDef: ColumnDef<[[ Camel ]]Record>[] = [
[% for col in list_columns %]
[% if col.component == 'select' and col.dict_code %]
    {
      accessorKey: '[[ col.field ]]',
      header: '[[ col.title ]]',
      cell: ({ row }) => dictLabel[[ col.dict_code|camel ]](row.original.[[ col.field ]]),
    },
[% else %]
    { accessorKey: '[[ col.field ]]', header: '[[ col.title ]]' },
[% endif %]
[% endfor %]
  ]

  const params: Record<string, unknown> = { page, page_size: pageSize, ...search }

  const listQuery = useQuery({
    queryKey: ['[[ code ]]-list', params],
    queryFn: () => [[ camel ]]Api.list(params),
  })

  const table = useReactTable({
    data: listQuery.data?.items ?? [],
    columns: columnsDef,
    getCoreRowModel: getCoreRowModel(),
  })

  const form = useForm<FormValues>({
    // zod coerce 输入输出类型不一致，这里做一次断言抹平
    resolver: zodResolver(formSchema) as unknown as Resolver<FormValues>,
    defaultValues: [[ form_defaults ]],
  })

  function openCreate() {
    setEditing(null)
    form.reset([[ form_defaults ]])
    setDialogOpen(true)
  }

  function openEdit(row: [[ Camel ]]Record) {
    setEditing(row)
    form.reset({[% for f in form_fields %][[ f.field ]]: row.[[ f.field ]] ?? [[ f.default_value ]][% if not loop.last %], [% endif %][% endfor %] })
    setDialogOpen(true)
  }

  const saveMutation = useMutation({
    mutationFn: (values: FormValues) =>
      editing ? [[ camel ]]Api.update(editing.id, values) : [[ camel ]]Api.create(values),
    onSuccess: () => {
      toast.success(editing ? '修改成功' : '新增成功')
      setDialogOpen(false)
      queryClient.invalidateQueries({ queryKey: ['[[ code ]]-list'] })
    },
    onError: (error: Error) => toast.error(error.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => [[ camel ]]Api.remove(id),
    onSuccess: () => {
      toast.success('删除成功')
      setDeleting(null)
      queryClient.invalidateQueries({ queryKey: ['[[ code ]]-list'] })
    },
    onError: (error: Error) => toast.error(error.message),
  })

  const total = listQuery.data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  return (
    <div className="space-y-4">
      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 py-4">
[% for col in search_columns %]
          <Input
            placeholder="按[[ col.title ]]搜索"
            className="w-48"
            value={search['[[ col.field ]]'] ?? ''}
            onChange={(e) => {
              setSearch((s) => ({ ...s, [[ col.field ]]: e.target.value }))
              setPage(1)
            }}
          />
[% endfor %]
          <Auth code="[[ code ]]:add">
            <Button onClick={openCreate}>
              <Plus className="size-4" />
              新增[[ name ]]
            </Button>
          </Auth>
          <span className="ml-auto text-sm text-muted-foreground">共 {total} 条</span>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                {table.getHeaderGroups()[0]?.headers.map((header) => (
                  <TableHead key={header.id}>
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
                <TableHead className="w-32 text-right">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {listQuery.isLoading ? (
                <TableRow>
                  <TableCell colSpan={columnsDef.length + 1} className="h-24 text-center">
                    加载中...
                  </TableCell>
                </TableRow>
              ) : table.getRowModel().rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={columnsDef.length + 1} className="h-24 text-center">
                    暂无数据
                  </TableCell>
                </TableRow>
              ) : (
                table.getRowModel().rows.map((row) => (
                  <TableRow key={row.original.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell ?? null, cell.getContext())}
                      </TableCell>
                    ))}
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Auth code="[[ code ]]:update">
                          <Button variant="ghost" size="sm" onClick={() => openEdit(row.original)}>
                            <Pencil className="size-4" />
                          </Button>
                        </Auth>
                        <Auth code="[[ code ]]:delete">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-destructive hover:text-destructive"
                            onClick={() => setDeleting(row.original)}
                          >
                            <Trash2 className="size-4" />
                          </Button>
                        </Auth>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="flex items-center justify-end gap-2">
        <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          上一页
        </Button>
        <span className="text-sm text-muted-foreground">
          {page} / {totalPages}
        </span>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          下一页
        </Button>
      </div>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? '编辑[[ name ]]' : '新增[[ name ]]'}</DialogTitle>
          </DialogHeader>
          <Form {...form}>
            <form
              onSubmit={form.handleSubmit((values) => saveMutation.mutate(values))}
              className="space-y-4"
            >
[% for f in form_fields %]
              <FormField
                control={form.control}
                name="[[ f.field ]]"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>[[ f.title ]][% if f.required %]<span className="text-destructive">*</span>[% endif %]</FormLabel>
                    <FormControl>
[% if f.component == 'select' %]
                      <Select onValueChange={field.onChange} value={String(field.value ?? '')}>
                        <SelectTrigger className="w-full">
                          <SelectValue placeholder="请选择[[ f.title ]]" />
                        </SelectTrigger>
                        <SelectContent>
                          {(dict[[ f.dict_code|camel ]] ?? []).map((item) => (
                            <SelectItem key={item.value} value={item.value}>
                              {item.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
[% elif f.component == 'switch' %]
                      <Switch
                        checked={Boolean(field.value)}
                        onCheckedChange={field.onChange}
                      />
[% elif f.component == 'number' %]
                      <Input type="number" placeholder="请输入[[ f.title ]]" {...field} />
[% else %]
                      <Input placeholder="请输入[[ f.title ]]" {...field} />
[% endif %]
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
[% endfor %]
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                  取消
                </Button>
                <Button type="submit" disabled={saveMutation.isPending}>
                  {saveMutation.isPending ? '保存中...' : '确定'}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        </DialogContent>
      </Dialog>

      <Dialog open={!!deleting} onOpenChange={(open) => !open && setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            确定删除该[[ name ]]记录吗？此操作不可恢复。
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleting(null)}>
              取消
            </Button>
            <Button
              variant="destructive"
              disabled={deleteMutation.isPending}
              onClick={() => deleting && deleteMutation.mutate(deleting.id)}
            >
              {deleteMutation.isPending ? '删除中...' : '删除'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
